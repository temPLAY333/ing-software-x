import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { HomeComponent } from './components/home/home.component';
import { MensajePrivadoComponent } from './components/mensaje-privado/mensaje-privado.component';
import { MensajesPropiosComponent } from './components/mensajes-propios/mensajes-propios.component';
import { SeguidoresComponent } from './components/seguidores/seguidores.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'mensajes-propios', component: MensajesPropiosComponent },
  { path: 'seguidores', component: SeguidoresComponent },
  { path: 'mensajes-privados', component: MensajePrivadoComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}

