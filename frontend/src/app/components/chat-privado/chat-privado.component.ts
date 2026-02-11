import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Subscription } from 'rxjs';

import { 
  MensajesPrivadosService, 
  MensajePrivado, 
  Usuario 
} from '../../services/mensajes-privados.service';

@Component({
  selector: 'app-chat-privado',
  templateUrl: './chat-privado.component.html',
  styleUrls: ['./chat-privado.component.css']
})
export class ChatPrivadoComponent implements OnInit, OnDestroy {
  @ViewChild('mensajesContainer') private mensajesContainer!: ElementRef;

  currentUserId = '';
  conversacionActual: MensajePrivado[] = [];
  usuarioSeleccionado: Usuario | null = null;
  
  // Formulario
  mensajeForm: FormGroup;
  
  // Estados de carga
  cargandoMensajes = false;
  enviandoMensaje = false;
  
  // Paginación
  paginaActual = 0;
  hayMasMensajes = false;
  readonly MENSAJES_POR_PAGINA = 50;
  
  // Subscripciones
  private subscriptions: Subscription[] = [];
  private sseConnection: EventSource | null = null;

  constructor(
    private mensajesService: MensajesPrivadosService,
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router
  ) {
    // Formulario de mensaje
    this.mensajeForm = this.fb.group({
      texto: ['', [
        Validators.required,
        Validators.maxLength(1000),
        Validators.minLength(1)
      ]]
    });
  }

  ngOnInit(): void {
    this.cargarUsuarioActual();

    // Obtener ID del usuario desde la ruta
    const userId = this.route.snapshot.paramMap.get('userId');
    if (userId) {
      this.cargarUsuarioYConversacion(userId);
    } else {
      // Si no hay userId en la ruta, volver a la lista
      this.router.navigate(['/mensajes-privados']);
    }

    // Suscribirse a nuevos mensajes
    const nuevoMensajeSub = this.mensajesService.nuevoMensaje$.subscribe(mensaje => {
      if (mensaje && this.usuarioSeleccionado) {
        const esDelUsuario = mensaje.emisor.id === this.usuarioSeleccionado.id;
        const esParaElUsuario = mensaje.receptor.id === this.usuarioSeleccionado.id;
        
        if (esDelUsuario || esParaElUsuario) {
          this.conversacionActual.push(mensaje);
          this.scrollToBottom();
        }
      }
    });
    this.subscriptions.push(nuevoMensajeSub);

    // Conectar a SSE para notificaciones en tiempo real
    this.sseConnection = this.mensajesService.conectarSSE();
  }

  private cargarUsuarioActual(): void {
    try {
      const stored = localStorage.getItem('user');
      if (stored) {
        const parsed = JSON.parse(stored);
        this.currentUserId = parsed?.id || '';
      }
    } catch (error) {
      console.error('Error al leer usuario actual:', error);
    }
  }

  private cargarUsuarioYConversacion(userId: string): void {
    // Primero buscar el usuario para obtener su información
    this.mensajesService.buscarUsuarios('').subscribe({
      next: (usuarios) => {
        const usuario = usuarios.find(u => u.id === userId);
        if (usuario) {
          this.usuarioSeleccionado = usuario;
          this.cargarMensajes();
        } else {
          // Si no se encuentra el usuario, intentar cargar la conversación de todos modos
          // Esto puede pasar si el usuario viene de la lista de conversaciones
          this.cargarConversacionDirecta(userId);
        }
      },
      error: () => {
        // En caso de error, intentar cargar la conversación de todos modos
        this.cargarConversacionDirecta(userId);
      }
    });
  }

  private cargarConversacionDirecta(userId: string): void {
    // Crear un usuario temporal con la información mínima
    this.usuarioSeleccionado = {
      id: userId,
      nickName: 'Usuario',
      nombre: '',
      apellido: '',
      fotoUsuario: ''
    };
    this.cargarMensajes();
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
    
    if (this.sseConnection) {
      this.sseConnection.close();
    }
  }

  /**
   * Cargar mensajes de la conversación
   */
  cargarMensajes(): void {
    if (!this.usuarioSeleccionado) return;

    this.cargandoMensajes = true;
    
    this.mensajesService.obtenerConversacion(
      this.usuarioSeleccionado.id,
      this.MENSAJES_POR_PAGINA,
      this.paginaActual * this.MENSAJES_POR_PAGINA
    ).subscribe({
      next: (data) => {
        this.conversacionActual = [
          ...this.conversacionActual,
          ...data.conversacion
        ];
        this.hayMasMensajes = data.hasMore;
        this.cargandoMensajes = false;
        
        // Si obtuvimos información del usuario en la respuesta, actualizar
        if (data.conversacion.length > 0 && this.usuarioSeleccionado) {
          const primerMensaje = data.conversacion[0];
          if (primerMensaje.emisor.id === this.usuarioSeleccionado.id) {
            this.usuarioSeleccionado = primerMensaje.emisor;
          } else if (primerMensaje.receptor.id === this.usuarioSeleccionado.id) {
            this.usuarioSeleccionado = primerMensaje.receptor;
          }
        }
        
        // Scroll al final en la primera carga
        if (this.paginaActual === 0) {
          setTimeout(() => this.scrollToBottom(), 100);
        }
      },
      error: (error) => {
        console.error('Error al cargar mensajes:', error);
        this.cargandoMensajes = false;
      }
    });
  }

  /**
   * Cargar más mensajes (scroll infinito hacia arriba)
   */
  cargarMasMensajes(): void {
    if (this.cargandoMensajes || !this.hayMasMensajes) return;
    
    this.paginaActual++;
    this.cargarMensajes();
  }

  /**
   * Enviar mensaje
   */
  enviarMensaje(): void {
    if (this.mensajeForm.invalid || !this.usuarioSeleccionado) return;

    const texto = this.mensajeForm.get('texto')?.value.trim();
    if (!texto) return;

    this.enviandoMensaje = true;
    this.mensajeForm.get('texto')?.disable();

    this.mensajesService.enviarMensaje(this.usuarioSeleccionado.id, texto).subscribe({
      next: (mensaje) => {
        // No agregamos el mensaje aquí porque el SSE lo manejará automáticamente
        // this.conversacionActual.push(mensaje);
        this.mensajeForm.reset();
        this.scrollToBottom();
        
        this.enviandoMensaje = false;
        this.mensajeForm.get('texto')?.enable();
      },
      error: (error) => {
        console.error('Error al enviar mensaje:', error);
        alert(error.message || 'Error al enviar mensaje');
        this.enviandoMensaje = false;
        this.mensajeForm.get('texto')?.enable();
      }
    });
  }

  /**
   * Scroll al final del contenedor de mensajes
   */
  private scrollToBottom(): void {
    try {
      if (this.mensajesContainer) {
        const element = this.mensajesContainer.nativeElement;
        element.scrollTop = element.scrollHeight;
      }
    } catch (err) {
      console.error('Error al hacer scroll:', err);
    }
  }

  /**
   * Formatear fecha del mensaje
   */
  formatearFecha(fecha: string): string {
    const date = new Date(fecha);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    
    if (seconds < 60) return 'Ahora';
    if (seconds < 3600) return `Hace ${Math.floor(seconds / 60)}m`;
    if (seconds < 86400) return `Hace ${Math.floor(seconds / 3600)}h`;
    if (seconds < 604800) return `Hace ${Math.floor(seconds / 86400)}d`;
    
    return date.toLocaleDateString();
  }

  /**
   * Obtener clases CSS para el mensaje
   */
  obtenerClasesMensaje(mensaje: MensajePrivado): string {
    const esPropio = mensaje.emisor.id === this.currentUserId;
    return esPropio ? 'mensaje-propio' : 'mensaje-ajeno';
  }

  /**
   * Verificar si el formulario es válido
   */
  get puedeEnviar(): boolean {
    return this.mensajeForm.valid && 
           !this.enviandoMensaje && 
           !!this.usuarioSeleccionado;
  }

  /**
   * Obtener longitud del texto actual
   */
  get longitudTexto(): number {
    return this.mensajeForm.get('texto')?.value?.length || 0;
  }
}
