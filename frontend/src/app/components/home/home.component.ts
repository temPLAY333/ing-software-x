import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  usuarioNickname = 'juanperez';
  usuarioBNickname = 'mariagarcia';
  cargando = false;
  cargandoUsuarioA = false;
  cargandoUsuarioB = false;
  error: string | null = null;

  constructor(
    public authService: AuthService, // Cambiar a public para usar en el template
    private router: Router,
    private http: HttpClient
  ) { }

  ngOnInit(): void {
    // Siempre mostrar el Home, no redirigir automáticamente
    // El usuario debe hacer clic en el botón para autenticarse
  }

  entrarComoUsuario(): void {
    this.entrarComoUsuarioPorNickname(this.usuarioNickname, 'cargandoUsuarioA');
  }

  entrarComoUsuarioB(): void {
    this.entrarComoUsuarioPorNickname(this.usuarioBNickname, 'cargandoUsuarioB');
  }

  private entrarComoUsuarioPorNickname(nickname: string, loadingFlag: 'cargandoUsuarioA' | 'cargandoUsuarioB'): void {
    if (loadingFlag === 'cargandoUsuarioA') {
      this.cargandoUsuarioA = true;
    } else {
      this.cargandoUsuarioB = true;
    }
    this.error = null;

    // Obtener token del backend
    const url = `${environment.apiUrl}/testing/token/${nickname}`;
    
    this.http.get<any>(url).subscribe({
      next: (response) => {
        if (response.success && response.data) {
          // Guardar token y usuario
          const token = response.data.token;
          const user = response.data.user;
          
          localStorage.setItem('access_token', token);
          localStorage.setItem('user', JSON.stringify(user));
          
          console.log('✅ Autenticado como:', user.nickName);
          
          // Redirigir a mensajes propios
          this.router.navigate(['/mensajes-propios']);
        } else {
          this.error = 'No se pudo obtener el token del servidor';
          if (loadingFlag === 'cargandoUsuarioA') {
            this.cargandoUsuarioA = false;
          } else {
            this.cargandoUsuarioB = false;
          }
        }
      },
      error: (err) => {
        console.error('Error al autenticarse:', err);
        this.error = err.error?.error || 'Error al conectarse con el servidor';
        if (loadingFlag === 'cargandoUsuarioA') {
          this.cargandoUsuarioA = false;
        } else {
          this.cargandoUsuarioB = false;
        }
      }
    });
  }
}

