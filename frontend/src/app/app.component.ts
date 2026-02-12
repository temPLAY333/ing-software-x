import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { AuthService } from './services/auth.service';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  mostrarNavbar = true;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Usuario ya está inicializado en el constructor del servicio
    
    // Ocultar navbar en el chat de mensajes privados y en home
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      this.mostrarNavbar = !event.url.includes('/chat-privado') && event.url !== '/' && event.url !== '/home';
    });

    // Verificar ruta inicial
    this.mostrarNavbar = !this.router.url.includes('/chat-privado') && this.router.url !== '/' && this.router.url !== '/home';
  }

  tieneToken(): boolean {
    return this.authService.isAuthenticated();
  }
}

