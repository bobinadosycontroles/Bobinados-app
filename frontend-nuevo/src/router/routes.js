
const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'index', component: () => import('pages/IndexPage.vue'), meta: { requiresAuth: true } },
      { path: 'usuarios', name: 'usuarios', component: () => import('pages/UsuariosPage.vue'), meta: { requiresAuth: true } },
      { path: 'inventario', name: 'inventario', component: () => import('pages/InventarioPage.vue'), meta: { requiresAuth: true } },
      { path: 'taller/ingreso', name: 'taller-stage-1', component: () => import('pages/TallerIngresosPage.vue'), meta: { requiresAuth: true, stage: 1 } },
      { path: 'taller/revision', name: 'taller-stage-2', component: () => import('pages/TallerIngresosPage.vue'), meta: { requiresAuth: true, stage: 2 } },
      { path: 'taller/procedimiento', name: 'taller-stage-3', component: () => import('pages/TallerIngresosPage.vue'), meta: { requiresAuth: true, stage: 3 } },
      { path: 'taller/entrega', name: 'taller-stage-4', component: () => import('pages/TallerIngresosPage.vue'), meta: { requiresAuth: true, stage: 4 } },
      { path: 'clientes', name: 'clientes', component: () => import('pages/ClientesPage.vue'), meta: { requiresAuth: true } },
      { path: 'parametros', name: 'parametros', component: () => import('pages/ParametrosPage.vue'), meta: { requiresAuth: true } }
    ]
  },
  { path: '/login', name: 'login', component: () => import('pages/LoginPage.vue') }
]

// Always leave this as last one
if (process.env.MODE !== 'ssr') {
  routes.push({
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  })
}

export default routes

