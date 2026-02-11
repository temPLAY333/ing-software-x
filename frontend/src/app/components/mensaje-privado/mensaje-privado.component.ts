import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';

import { 
  MensajesPrivadosService, 
  Usuario 
} from '../../services/mensajes-privados.service';

@Component({
  selector: 'app-mensaje-privado',
  templateUrl: './mensaje-privado.component.html',
  styleUrls: ['./mensaje-privado.component.css']
})
export class MensajePrivadoComponent implements OnInit, OnDestroy {
  @ViewChild('searchInput') private searchInput!: ElementRef;

  // Conversaciones
  conversaciones: any[] = [];
  
  // Formulario de búsqueda
  searchForm: FormGroup;
  
  // Búsqueda de usuarios
  usuariosBuscados: Usuario[] = [];
  buscandoUsuarios = false;
  
  // Estados de carga
  cargandoConversaciones = false;
  
  // Subscripciones
  private subscriptions: Subscription[] = [];
  private sseConnection: EventSource | null = null;

  constructor(
    private mensajesService: MensajesPrivadosService,
    private fb: FormBuilder,
    private router: Router
  ) {
    // Formulario de búsqueda
    this.searchForm = this.fb.group({
      busqueda: ['']
    });
  }

  ngOnInit(): void {
    // Cargar lista de conversaciones
    this.cargarConversaciones();

    // Configurar búsqueda con debounce
    const searchSub = this.searchForm.get('busqueda')?.valueChanges
      .pipe(
        debounceTime(300),
        distinctUntilChanged()
      )
      .subscribe(valor => {
        if (valor && valor.length >= 2) {
          this.buscarUsuarios(valor);
        } else {
          this.usuariosBuscados = [];
        }
      });
    
    if (searchSub) {
      this.subscriptions.push(searchSub);
    }

    // Conectar a SSE para notificaciones en tiempo real
    this.sseConnection = this.mensajesService.conectarSSE();
  }

  ngOnDestroy(): void {
    // Limpiar subscripciones
    this.subscriptions.forEach(sub => sub.unsubscribe());
    
    // Cerrar conexión SSE
    if (this.sseConnection) {
      this.sseConnection.close();
    }
  }

  /**
   * Cargar lista de conversaciones
   */
  cargarConversaciones(): void {
    this.cargandoConversaciones = true;
    
    this.mensajesService.listarConversaciones().subscribe({
      next: (conversaciones) => {
        this.conversaciones = conversaciones;
        this.cargandoConversaciones = false;
      },
      error: (error) => {
        console.error('Error al cargar conversaciones:', error);
        this.cargandoConversaciones = false;
      }
    });
  }

  /**
   * Abrir conversación con un usuario
   */
  abrirConversacion(usuario: Usuario): void {
    this.router.navigate(['/chat-privado', usuario.id]);
  }

  /**
   * Buscar usuarios
   */
  buscarUsuarios(busqueda: string): void {
    this.buscandoUsuarios = true;
    
    this.mensajesService.buscarUsuarios(busqueda).subscribe({
      next: (usuarios) => {
        this.usuariosBuscados = usuarios;
        this.buscandoUsuarios = false;
      },
      error: (error) => {
        console.error('Error al buscar usuarios:', error);
        this.buscandoUsuarios = false;
      }
    });
  }

  enfocarBusqueda(): void {
    if (this.searchInput?.nativeElement) {
      this.searchInput.nativeElement.focus();
    }
  }

  /**
   * Seleccionar usuario de la búsqueda
   */
  seleccionarUsuario(usuario: Usuario): void {
    this.usuariosBuscados = [];
    this.searchForm.reset();
    this.abrirConversacion(usuario);
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
}

