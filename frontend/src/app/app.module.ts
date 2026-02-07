import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { ReactiveFormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { MensajePrivadoComponent } from './components/mensaje-privado/mensaje-privado.component';
import { MensajesPropiosComponent } from './components/mensajes-propios/mensajes-propios.component';
import { SeguidoresComponent } from './components/seguidores/seguidores.component';

@NgModule({
  declarations: [
    AppComponent,
    MensajePrivadoComponent,
    MensajesPropiosComponent,
    SeguidoresComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    ReactiveFormsModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {}

