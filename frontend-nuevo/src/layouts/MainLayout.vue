<template>
  <q-layout view="hHh lpR fFf">

    <q-header elevated class="bg-primary text-white navbar-bobinados">
      <q-toolbar class="navbar-toolbar">
        <div class="navbar-left">
          <div class="navbar-logo">
            <img src="/logo.png" class="navbar-logo-img" alt="Bobinados logo" />
          </div>
        </div>

        <div class="navbar-center row items-center no-wrap q-gutter-sm">
          <q-btn flat dense class="nav-link" :to="{ name: 'index' }" :class="{ 'nav-link-active': route.name === 'index' }" label="Inicio" />
          <q-btn flat dense class="nav-link" :to="{ name: 'usuarios' }" :class="{ 'nav-link-active': route.name === 'usuarios' }" label="Usuarios" />
          <q-btn flat dense class="nav-link" :to="{ name: 'inventario' }" :class="{ 'nav-link-active': route.name === 'inventario' }" label="Inventario" />
          <q-btn-dropdown
            flat
            dense
            class="nav-link"
            :class="{ 'nav-link-active': route.name?.startsWith('taller-stage-') }"
            label="Taller"
          >
            <q-list class="taller-menu-list">
              <q-item clickable v-close-popup :to="{ name: 'taller-stage-1' }">
                <q-item-section>Ingreso</q-item-section>
              </q-item>
              <q-item clickable v-close-popup :to="{ name: 'taller-stage-2' }">
                <q-item-section>Revisión</q-item-section>
              </q-item>
              <q-item clickable v-close-popup :to="{ name: 'taller-stage-3' }">
                <q-item-section>Procedimiento</q-item-section>
              </q-item>
              <q-item clickable v-close-popup :to="{ name: 'taller-stage-4' }">
                <q-item-section>Entrega</q-item-section>
              </q-item>
            </q-list>
          </q-btn-dropdown>
          <q-btn flat dense class="nav-link" :to="{ name: 'clientes' }" :class="{ 'nav-link-active': route.name === 'clientes' }" label="CLIENTES" />
          <q-btn flat dense class="nav-link" :to="{ name: 'parametros' }" :class="{ 'nav-link-active': route.name === 'parametros' }" label="Parametros" />
        </div>

        <q-space />

        <div class="navbar-right q-gutter-md row items-center no-wrap">
          <q-btn-dropdown flat dense rounded icon="person" color="accent" :label="full_name" label-color="white" class="profile-dropdown">
            <q-list style="min-width: 220px">
              <q-item clickable @click="editing" v-ripple>
                <q-item-section avatar>
                  <q-icon name="edit" color="primary" />
                </q-item-section>
                <q-item-section>Mi perfil</q-item-section>
              </q-item>
              <q-separator />
              <q-item clickable @click="logout" v-ripple>
                <q-item-section avatar>
                  <q-icon name="logout" color="negative" />
                </q-item-section>
                <q-item-section>Cerrar sesión</q-item-section>
              </q-item>
            </q-list>
          </q-btn-dropdown>
        </div>
      </q-toolbar>
    </q-header>

    <q-dialog v-model="toolbar">
      <q-card style="width: 700px; max-width: 80vw;" class="profile-card">
        <q-card-section class="row items-center bg-primary text-white">
          <div class="text-h6">Mi perfil</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-banner class="bg-grey-3">
          <template v-slot:avatar>
            <q-icon name="warning" color="warning" />
          </template>
          Los campos marcados con (*) son obligatorios
        </q-banner>

        <q-card-section>
          <q-form ref="form_ref">
            <div class="row justify-around">
              <div class="col-md-5">
                <q-input filled v-model="first_name" label="Nombres *" lazy-rules
                  :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
              </div>
              <div class="col-md-5">
                <q-input filled v-model="last_name" label="Apellidos *" lazy-rules
                  :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
              </div>
            </div>

            <div class="row justify-around">
              <div class="col-md-11">
                <q-input autocomplete="off" filled v-model="email" label="Correo electrónico *" lazy-rules
                  :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
              </div>
            </div>

            <div class="row justify-around">
              <div v-if="nuevo_password" class="col-md-5">
                <q-input autocomplete="off" type="password" filled v-model="actual_password" label="Contraseña *"
                  lazy-rules :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
              </div>
              <div v-else class="col-md-5">
                <q-input autocomplete="off" type="password" filled v-model="actual_password" label="Contraseña" />
              </div>
              <div class="col-md-5">
                <q-input autocomplete="off" type="password" filled v-model="nuevo_password"
                  label="Nueva contraseña *" />
              </div>
            </div>
          </q-form>
        </q-card-section>

        <q-card-actions align="right" class="bg-white text-teal">
          <q-btn label="Actualizar" @click.prevent="onEdit" color="primary" />
          <q-btn label="Cancelar" v-close-popup color="negative" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-page-container>
      <router-view />
    </q-page-container>

  </q-layout>

</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { api } from 'src/boot/axios'
import { useAuthStore } from 'src/stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { AbilityBuilder } from '@casl/ability'
import { ability } from 'src/services/ability'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

// Constante de path para la API
const path = 'seguridad/perfil/'

const toolbar = ref(false)
const first_name = ref(null)
const last_name = ref(null)
const email = ref(null)
const actual_password = ref(null)
const nuevo_password = ref(null)
const full_name = ref('')
const form_ref = ref(null)

async function logout() {
  try {
    auth.logout();
    router.push('/login');
  } catch (error) {
    console.error('Error al cerrar sesión', error);
  }
}

async function loadUser() {

  const response = await api.get(path)

  first_name.value = response.data.first_name
  last_name.value = response.data.last_name
  email.value = response.data.email
  full_name.value = first_name.value + ' ' + last_name.value
}



function editing() {

  toolbar.value = true
  actual_password.value = null
  nuevo_password.value = null
}

async function onEdit() {

  const success = await form_ref.value.validate()
  if (!success) return

  await api.put(path, {
    first_name: first_name.value,
    last_name: last_name.value,
    email: email.value,
    actual_password: actual_password.value,
    nuevo_password: nuevo_password.value
  })

  toolbar.value = false
  loadUser()
}

function setAbilities(rol) {
  if (!rol) return

  const { can, rules } = new AbilityBuilder(ability.constructor)

  switch (rol) {
    case 'AD':
      can('manage', 'all')
      break
    case 'CO':
      can(['read'], ['Taller', 'Inventario'])
      break
    case 'IN':
      can(['read'], ['Taller', 'Inventario'])
      can(['create', 'update', 'delete', 'detail', 'finish'], 'Taller')
      break
    case 'PR':
      can(['read'], ['Taller', 'Inventario'])
      break
    case 'PL':
      can(['read'], ['Taller', 'Inventario'])
      break
    default:
      break
  }

  ability.update(rules)
}

onMounted(() => {
  loadUser();
  setAbilities(auth.rol)
})

watch(() => auth.rol, rol => {
  setAbilities(rol)
})
</script>

<style lang="scss">
.cursor {
  cursor: pointer;
}

// Navbar BOBINADOS styles
.navbar-bobinados {
  background: linear-gradient(135deg, var(--bobinados-primary) 0%, rgba(0,34,68,0.95) 100%);
  border-bottom: 3px solid var(--bobinados-accent);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
  animation: navbar-slide 420ms ease forwards;

  .navbar-toolbar {
    padding: 8px 16px;
  }

  .navbar-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .navbar-logo {
    display: flex;
    align-items: center;
    gap: 12px;
    font-weight: 600;
    font-size: 18px;
    letter-spacing: 1px;

    .navbar-title {
      color: #ffffff;
      font-weight: 700;
      font-size: 1rem;
    }

    .navbar-tagline {
      color: rgba(255,255,255,0.88);
      font-size: 0.9rem;
      letter-spacing: 0.4px;
    }

    .navbar-logo-img {
      height: 40px;
      transition: transform 250ms ease, filter 250ms ease;
      will-change: transform;
    }

    &:hover .navbar-logo-img {
      transform: scale(1.08) rotate(-2deg);
      filter: drop-shadow(0 8px 18px rgba(0,0,0,0.25));
    }
  }

  .navbar-menu-btn {
    color: #ffffff;

    &:hover {
      background-color: rgba(212, 175, 55, 0.2);
    }
  }

  .navbar-center {
    display: flex;
    align-items: center;
    gap: 6px;
    overflow-x: auto;
    padding: 4px 0;
    flex-wrap: nowrap;
    scrollbar-width: none;
  }

  .navbar-center::-webkit-scrollbar {
    display: none;
  }

  .nav-link {
    min-width: 120px;
    color: rgba(255,255,255,0.82);
    font-weight: 600;
    transition: color 210ms ease, transform 210ms ease;
    position: relative;
  }

  .nav-link:hover {
    color: #ffffff;
    transform: translateY(-1px);
  }

  .nav-link::after {
    content: '';
    position: absolute;
    inset: auto 0 0;
    left: 20%;
    right: 20%;
    height: 3px;
    background: transparent;
    border-radius: 999px;
    transition: background 210ms ease, transform 210ms ease;
    transform: scaleX(0.4);
  }

  .nav-link-active {
    color: #ffffff !important;
  }

  .nav-link-active::after {
    background: linear-gradient(90deg, #f8e71c, #ff8a00);
    transform: scaleX(1);
  }

  .navbar-right {
    .q-btn-dropdown {
      &:hover {
        background-color: rgba(212, 175, 55, 0.12);
      }
    }
  }
}

@keyframes navbar-slide {
  from { transform: translateY(-12px); opacity: 0 }
  to { transform: translateY(0); opacity: 1 }
}

/* Underline effect on navigation items */
.nav-link::after,
.nav-link:hover::after {
  content: '';
  display: block;
  height: 3px;
  width: 60%;
  background: transparent;
  margin-top: 6px;
  border-radius: 999px;
  transition: all 220ms ease;
}

.drawer-bobinados {
  background-color: #f5f5f5;
  border-right: 3px solid #D4AF37;

  .drawer-header {
    color: #003366;
    font-weight: 700;
    background-color: #f0f0f0;
    border-bottom: 2px solid #D4AF37;
  }

  .q-item {
    &:hover {
      background-color: rgba(0, 51, 102, 0.08);
    }

    &.drawer-active {
      background-color: #003366;
      color: white;
      font-weight: 600;

      .q-icon {
        color: #D4AF37;
      }

      &:before {
        left: 0;
        width: 4px;
        height: 100%;
        background-color: #C41E3A;
      }
    }
  }
}

// Profile card
.profile-card {
  border-top: 4px solid #D4AF37;
}
</style>
