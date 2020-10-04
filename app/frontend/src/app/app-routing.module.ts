import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { VizComponent } from './viz/viz.component';
import { PredictionComponent } from './prediction/prediction.component';

const routes: Routes = [
  { path: '', redirectTo: '/past', pathMatch: 'full' },
  { path: 'past', component: VizComponent },
  { path: 'prediction', component: VizComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
