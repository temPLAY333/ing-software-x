import { Component, OnInit } from '@angular/core';
import { SeguidoresService, Usuario } from '../../services/seguidores.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-seguidores',
  templateUrl: './seguidores.component.html',
  styleUrls: ['./seguidores.component.css']
})
export class SeguidoresComponent implements OnInit {
  usuarioActual: any = null;
  seguidores: Usuario[] = [];
  cargando = false;
  error: string | null = null;
  vistaActiva: 'seguidores' | 'siguiendo' = 'seguidores';

  constructor(
    private seguidoresService: SeguidoresService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.usuarioActual = this.authService.getCurrentUser();
    this.cargarSeguidores();
  }

  cambiarVista(vista: 'seguidores' | 'siguiendo'): void {
    this.vistaActiva = vista;
    // TODO: Implementar carga de siguiendo cuando esté disponible
    if (vista === 'seguidores') {
      this.cargarSeguidores();
    }
  }

  verPerfilUsuario(usuario: Usuario): void {
    // TODO: Navegar al perfil/home del usuario
    console.log('Ver perfil de:', usuario);
  }

  cargarSeguidores(): void {
    this.cargando = true;
    this.error = null;
    this.seguidoresService.obtenerSeguidores().subscribe({
      next: (seguidores) => {
        this.seguidores = seguidores;
        this.cargando = false;
      },
      error: (error) => {
        console.error('Error al cargar seguidores:', error);
        this.error = 'No se pudieron cargar los seguidores';
        this.cargando = false;
      }
    });
  }
}

