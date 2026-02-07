import { Component, OnInit } from '@angular/core';
import { MensajesService, Mensaje } from '../../services/mensajes.service';

@Component({
  selector: 'app-mensajes-propios',
  templateUrl: './mensajes-propios.component.html',
  styleUrls: ['./mensajes-propios.component.css']
})
export class MensajesPropiosComponent implements OnInit {
  mensajes: Mensaje[] = [];
  cargando = false;
  offset = 0;
  readonly limit = 20;
  hayMas = false;

  constructor(private mensajesService: MensajesService) {}

  ngOnInit(): void {
    this.cargarMensajes();
  }

  cargarMensajes(): void {
    this.cargando = true;
    this.mensajesService.obtenerMensajesPropios(this.limit, this.offset).subscribe({
      next: (data) => {
        this.mensajes = [...this.mensajes, ...data.mensajes];
        this.hayMas = data.hasMore;
        this.offset += this.limit;
        this.cargando = false;
      },
      error: (error) => {
        console.error('Error al cargar mensajes propios:', error);
        this.cargando = false;
      }
    });
  }
}

