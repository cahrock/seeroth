import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  template: `
    <div class="min-h-screen bg-gray-950 text-white flex items-center justify-center">
      <div class="text-center">
        <h1 class="text-4xl font-bold text-emerald-400">SeeRoth</h1>
        <p class="text-gray-400 mt-2">sirat al-mustaqim — The Straight Path to Halal Wealth</p>
        <p class="text-gray-600 mt-4 text-sm">v1.0.0 MVP — Loading...</p>
      </div>
    </div>
    <router-outlet />
  `,
})
export class AppComponent {
  title = 'seeroth-web';
}
