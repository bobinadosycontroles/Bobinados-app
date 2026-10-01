<template>
  <q-page class="q-pa-md clientes-page">
    <div class="page-header row items-center justify-between q-mb-md">
      <div>
        <div class="text-h4 text-primary">Clientes</div>
        <div class="text-caption text-grey-7">Gestión de clientes para integrar los ingresos del taller.</div>
      </div>
      <q-btn label="Agregar cliente" color="primary" unelevated @click="openDialog(false)" />
    </div>

    <q-card class="page-card">
      <q-card-section class="row items-center justify-between q-gutter-sm">
        <div class="text-subtitle1 text-weight-bold">Listado de clientes</div>
        <q-input dense outlined v-model="filter" placeholder="Buscar cliente" class="search-input">
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <div v-if="loading" class="row justify-center q-py-xl">
          <q-spinner color="primary" size="32px" />
        </div>

        <div v-else-if="filteredClientes.length" class="row q-col-gutter-md">
          <div v-for="cliente in filteredClientes" :key="cliente.uuid || cliente.id" class="col-xs-12 col-sm-6 col-md-4">
            <q-card bordered class="client-card">
              <q-card-section class="bg-grey-1">
                <div class="row items-center justify-between">
                  <div class="text-subtitle1 text-weight-bold">{{ cliente.nombre }}</div>
                  <q-chip color="primary" text-color="white" dense>Cliente</q-chip>
                </div>
              </q-card-section>

              <q-card-section>
                <div class="info-row"><q-icon name="badge" size="18px" class="q-mr-sm" />{{ cliente.documento || 'Documento no registrado' }}</div>
                <div class="info-row"><q-icon name="phone" size="18px" class="q-mr-sm" />{{ cliente.telefono || 'Teléfono no registrado' }}</div>
                <div class="info-row"><q-icon name="person" size="18px" class="q-mr-sm" />{{ cliente.contacto || 'Contacto no registrado' }}</div>
                <div class="info-row"><q-icon name="mail" size="18px" class="q-mr-sm" />{{ cliente.correo || 'Correo no registrado' }}</div>
                <div class="info-row"><q-icon name="location_on" size="18px" class="q-mr-sm" />{{ cliente.ciudad || 'Ciudad no registrada' }}</div>
              </q-card-section>

              <q-card-actions align="right">
                <q-btn flat color="primary" label="Editar" @click="openDialog(true, cliente)" />
                <q-btn flat color="negative" label="Eliminar" @click="deleteCliente(cliente)" />
              </q-card-actions>
            </q-card>
          </div>
        </div>

        <div v-else class="row justify-center q-py-xl">
          <div class="text-grey-7">No hay clientes registrados todavía.</div>
        </div>
      </q-card-section>
    </q-card>

    <q-dialog v-model="dialog" persistent>
      <q-card class="dialog-card">
        <q-card-section class="row items-center">
          <div class="text-h6">{{ editingId ? 'Editar cliente' : 'Nuevo cliente' }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup @click="closeDialog" />
        </q-card-section>

        <q-card-section>
          <q-form ref="formRef" @submit.prevent="submitCliente">
            <q-input filled v-model="form.nombre" label="Nombre del cliente *" lazy-rules :rules="[val => !!val || 'El campo es obligatorio']" />
            <q-input filled v-model="form.documento" label="Documento" />
            <q-input filled v-model="form.telefono" label="Teléfono" />
            <q-input filled v-model="form.contacto" label="Contacto" />
            <q-input filled v-model="form.correo" label="Correo" type="email" />
            <q-input filled v-model="form.ciudad" label="Ciudad" />
            <q-input filled v-model="form.direccion" label="Dirección" />
            <q-input filled v-model="form.observacion" label="Observación" type="textarea" rows="3" />
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="Cancelar" color="negative" flat @click="closeDialog" />
          <q-btn label="Guardar" color="primary" @click="submitCliente" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from 'src/boot/axios'
import Swal from 'sweetalert2'

const clientes = ref([])
const loading = ref(false)
const filter = ref('')
const dialog = ref(false)
const editingId = ref(null)
const formRef = ref(null)

const form = ref({
  nombre: '',
  documento: '',
  telefono: '',
  correo: '',
  ciudad: '',
  direccion: '',
  contacto: '',
  observacion: ''
})

const filteredClientes = computed(() => {
  const query = filter.value.trim().toLowerCase()
  if (!query) return clientes.value

  return clientes.value.filter((cliente) => {
    const fields = [cliente.nombre, cliente.documento, cliente.telefono, cliente.contacto, cliente.correo, cliente.ciudad]
    return fields.some((value) => String(value || '').toLowerCase().includes(query))
  })
})

onMounted(() => {
  loadClientes()
})

async function loadClientes() {
  loading.value = true
  try {
    const response = await api.get('core/cliente/')
    clientes.value = response.data
  } catch (error) {
    console.error(error)
    Swal.fire({ title: 'Error', text: 'No se pudieron cargar los clientes', icon: 'error' })
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.value = {
    nombre: '',
    documento: '',
    telefono: '',
    contacto: '',
    correo: '',
    ciudad: '',
    direccion: '',
    observacion: ''
  }
  editingId.value = null
}

function openDialog(isEdit = false, row = null) {
  if (isEdit && row) {
    form.value = {
      nombre: row.nombre || '',
      documento: row.documento || '',
      telefono: row.telefono || '',
      contacto: row.contacto || '',
      correo: row.correo || '',
      ciudad: row.ciudad || '',
      direccion: row.direccion || '',
      observacion: row.observacion || ''
    }
    editingId.value = row.uuid || row.id
  } else {
    resetForm()
  }
  dialog.value = true
}

function closeDialog() {
  dialog.value = false
  resetForm()
}

async function submitCliente() {
  if (!form.value.nombre) return

  try {
    const payload = {
      nombre: form.value.nombre,
      contacto: form.value.contacto,
      documento: form.value.documento,
      telefono: form.value.telefono,
      correo: form.value.correo,
      ciudad: form.value.ciudad,
      direccion: form.value.direccion,
      observacion: form.value.observacion
    }

    if (editingId.value) {
      await api.put(`core/cliente/${editingId.value}/`, payload)
      Swal.fire({ title: 'Éxito', text: 'Cliente actualizado', icon: 'success' })
    } else {
      await api.post('core/cliente/', payload)
      Swal.fire({ title: 'Éxito', text: 'Cliente creado', icon: 'success' })
    }

    dialog.value = false
    await loadClientes()
  } catch (error) {
    Swal.fire({ title: 'Error', text: error?.response?.data?.detail || 'No se pudo guardar el cliente', icon: 'error' })
  }
}

async function deleteCliente(row) {
  Swal.fire({
    title: '¿Está seguro?',
    text: `¿Desea eliminar el cliente ${row.nombre}?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d32f2f',
    cancelButtonColor: '#424242'
  }).then(async (result) => {
    if (result.isConfirmed) {
      try {
        await api.delete(`core/cliente/${row.uuid || row.id}/`)
        Swal.fire({ title: 'Éxito', text: 'Cliente eliminado', icon: 'success' })
        await loadClientes()
      } catch (error) {
        Swal.fire({ title: 'Error', text: error?.response?.data?.detail || 'No se pudo eliminar', icon: 'error' })
      }
    }
  })
}
</script>

<style scoped>
.clientes-page {
  min-height: calc(100vh - 64px);
  background: #f7f9ff;
}

.page-header {
  margin-bottom: 16px;
}

.page-card {
  border-radius: 18px;
  overflow: hidden;
}

.search-input {
  min-width: 260px;
}

.client-card {
  height: 100%;
  border-radius: 16px;
  transition: transform 180ms ease, box-shadow 180ms ease;
}

.client-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  color: #4b5563;
}

.dialog-card {
  width: min(92vw, 640px);
  border-radius: 18px;
}

@media (max-width: 600px) {
  .search-input {
    width: 100%;
    min-width: 0;
  }
}
</style>
