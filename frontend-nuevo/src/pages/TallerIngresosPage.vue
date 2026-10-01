<template>
  <q-page class="q-pa-md taller-page">
    <q-card class="taller-card">
      <q-card-section class="row items-center justify-between q-gutter-sm">
        <div>
          <div class="text-h5 text-primary">Taller - {{ stageLabel }}</div>
          <div class="text-caption text-grey-7">{{ stageDescription }}</div>
        </div>
        <div class="row items-center q-gutter-sm">
          <q-btn v-if="currentStage === 1" label="Agregar ingreso" color="primary" unelevated @click="openModal()" />
          <q-btn v-if="currentStage === 1" flat color="secondary" :icon="showClosedOrders ? 'visibility_off' : 'visibility'" :label="showClosedOrders ? 'Ver ingresos abiertos' : 'Ver ingresos cerrados'" @click="showClosedOrders = !showClosedOrders" />
        </div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <q-table
          :title="stageLabel"
          :rows="filteredIngresos"
          :columns="columns"
          row-key="uuid"
          dense
          flat
          bordered
          :pagination="pagination"
          v-model:pagination="pagination"
          :no-data-label="'No hay órdenes en esta etapa'"
        >
          <template v-slot:body="props">
            <q-tr :props="props">
              <q-td key="order_number" :props="props">{{ props.row.order_number || props.row.ingreso?.order_number || '-' }}</q-td>
              <q-td key="fecha" :props="props">{{ props.row.fecha || props.row.ingreso?.fecha || '-' }}</q-td>
              <q-td key="cliente" :props="props">{{ props.row.cliente?.nombre || props.row.ingreso?.cliente || props.row.ingreso?.cliente_uuid || '-' }}</q-td>
              <q-td key="motor" :props="props">{{ props.row.ingreso?.motor || '-' }}</q-td>
              <q-td key="servicio" :props="props">{{ props.row.ingreso?.servicio || '-' }}</q-td>
              <q-td key="telefono" :props="props">{{ props.row.ingreso?.telefono || '-' }}</q-td>
              <q-td key="actions" :props="props">
                <div class="row items-center no-wrap q-gutter-sm">
                  <template v-if="currentStage === 1">
                    <q-btn dense round flat icon="edit" color="primary" @click="openModal(props.row)" />
                    <q-btn dense round flat icon="delete_forever" color="negative" @click="deleteIngreso(props.row.uuid)" />
                  </template>

                  <template v-else-if="currentStage === 2">
                    <q-btn dense round flat icon="play_arrow" color="primary" v-if="props.row.status === 'ingreso'" @click="openModal(props.row)" />
                    <q-btn dense round flat icon="edit" color="primary" v-else @click="openModal(props.row)" />
                    <q-btn dense round flat icon="arrow_forward" color="secondary" v-if="props.row.status === 'revision'" @click="confirmAdvanceOrder(props.row)" />
                    <q-btn dense round flat icon="delete_forever" color="negative" @click="deleteIngreso(props.row.uuid)" />
                  </template>

                  <template v-else-if="currentStage === 3">
                    <q-btn dense round flat icon="play_arrow" color="primary" v-if="props.row.status === 'revision'" @click="openModal(props.row)" />
                    <q-btn dense round flat icon="edit" color="primary" v-else @click="openModal(props.row)" />
                    <q-btn dense round flat icon="delete_forever" color="negative" @click="deleteIngreso(props.row.uuid)" v-if="props.row.status !== 'ingreso'" />
                  </template>

                  <template v-else>
                    <q-btn dense round flat icon="local_shipping" color="primary" @click="openModal(props.row)" />
                    <q-btn dense round flat icon="delete_forever" color="negative" @click="deleteIngreso(props.row.uuid)" v-if="props.row.status === 'procedimiento'" />
                  </template>
                </div>
              </q-td>
            </q-tr>
          </template>
        </q-table>
      </q-card-section>
    </q-card>

    <q-dialog v-model="showModal" persistent>
      <q-card class="modal-card">
        <q-card-section class="row items-center q-pb-none">
          <div>
            <div class="text-h6">{{ currentStageLabel }}</div>
            <div class="text-caption text-grey-7">{{ currentOrderLabel }}</div>
          </div>
          <q-space />
          <q-btn v-if="currentStage === 1" icon="print" flat round dense color="primary" @click="printIngreso" />
          <q-btn icon="close" flat round dense @click="closeModal" />
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-form @submit.prevent="submitStage" class="q-gutter-md q-mt-sm">
            <div v-if="currentStage === 1" class="section-block">
              <div class="section-title">Ingreso</div>
              <div class="row q-col-gutter-md">
                <div class="col-xs-12 col-sm-3"><q-input filled v-model="ingresoForm.order_number" label="Número de orden" readonly dense /></div>
                <div class="col-xs-12 col-sm-3"><q-input filled v-model="ingresoForm.fecha" label="Fecha" type="date" dense /></div>
                <div class="col-xs-12 col-sm-4">
                  <q-select
                    filled
                    v-model="selectedClientUuid"
                    :options="clienteOptions"
                    label="Cliente"
                    emit-value
                    map-options
                    use-input
                    input-debounce="0"
                    dense
                    clearable
                    hide-dropdown-icon
                  />
                </div>
                <div class="col-xs-12 col-sm-4"><q-input filled v-model="ingresoForm.telefono" label="Teléfono" dense /></div>
                <div class="col-xs-12 col-sm-4"><q-input filled v-model="ingresoForm.cliente" label="Cliente manual" dense /></div>
              </div>
              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-12 text-right">
                  <div class="text-subtitle2">Total accesorios: <strong>{{ '$' + accessoriesTotal.toFixed(2) }}</strong></div>
                </div>
              </div>
              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-12 col-sm-3"><q-input filled v-model="ingresoForm.contacto" label="Contacto" dense /></div>
                <div class="col-xs-12 col-sm-3">
                  <q-select
                    filled
                    v-model="ingresoForm.motor"
                    :options="motorOptions"
                    label="Motor"
                    emit-value
                    map-options
                    dense
                  />
                </div>
                <div class="col-xs-12 col-sm-3"><q-input filled v-model="ingresoForm.serie" label="Serie" dense /></div>
                <div class="col-xs-12 col-sm-3">
                  <q-select
                    filled
                    v-model="ingresoForm.fases"
                    :options="fasesOptions"
                    label="Fases"
                    emit-value
                    map-options
                    dense
                    clearable
                  />
                </div>
              </div>
              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-12 col-sm-3">
                  <q-select
                    filled
                    v-model="ingresoForm.marca_choice"
                    :options="marcaOptions"
                    label="Marca"
                    emit-value
                    map-options
                    dense
                    @update:model-value="onMarcaSelect"
                  />
                </div>
              </div>
              <div class="row q-col-gutter-md q-mt-sm" v-if="ingresoForm.marca_choice === 'Otros'">
                <div class="col-xs-12 col-sm-6"><q-input filled v-model="ingresoForm.marca_custom" label="Marca - Otros" dense /></div>
              </div>
              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-12 col-sm-4"><q-input filled v-model="ingresoForm.aisl_cl" label="Aisl.Cl." dense /></div>
                <div class="col-xs-12 col-sm-4"><q-input filled v-model="ingresoForm.voltaje" label="Voltaje" dense /></div>
                <div class="col-xs-12 col-sm-4"><q-input filled v-model="ingresoForm.corriente" label="Corriente" dense /></div>
              </div>
              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-12 col-sm-4"><q-input filled v-model="ingresoForm.la_in" label="La/In" dense /></div>
                <div class="col-xs-12 col-sm-4"><q-input filled v-model="ingresoForm.cos" label="Cos" dense /></div>
                <div class="col-xs-12 col-sm-4"><q-input filled v-model="ingresoForm.servicio" label="Servicio" dense /></div>
              </div>
              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-12 col-sm-4"><q-input filled v-model="ingresoForm.h2" label="H2" dense /></div>
                <div class="col-xs-12 col-sm-4"><q-input filled v-model="ingresoForm.conexion_placa" label="Conexión en placa" dense /></div>
                <div class="col-xs-12 col-sm-4"><q-input filled v-model="ingresoForm.nro_puntas" label="Nro de puntas" dense /></div>
              </div>
              <div class="section-title q-mt-md">Condiciones Legales</div>
              <div class="legal-copy">
                <p><strong>NOTA: DEPÓSITO POR ALMACENAMIENTO Y ABANDONO DE BIENES</strong></p>
                <p>El cliente declara conocer y aceptar expresamente que, conforme a lo establecido en los Códigos Civil y de Comercio sobre el contrato de depósito, la retención del equipo o bien reparado que haya transcurrido un plazo de treinta (30) días calendario contados a partir de la fecha de recepción del equipo o de la cancelación del servicio, generará el cobro automático de un valor por DEPÓSITO Y ALMACENAMIENTO equivalente a DOS MIL PESOS COLOMBIANOS ($2.000 COP) diarios. Este valor se calculará de manera acumulativa por cada día que el bien permanezca en las instalaciones de la empresa.</p>
                <p><strong>PÉRDIDA DEL DERECHO DE RETIRO:</strong></p>
                <p>En caso de que el valor total acumulado por concepto de depósito iguale o supere el valor comercial del equipo reparado, el cliente perderá automáticamente el derecho a retirarlo, salvo que realice el pago previo y total de los valores adeudados por almacenamiento, reparación y demás costos generados. La empresa se reserva el derecho de retener el bien hasta el pago completo de la obligación.</p>
                <p><strong>PRESUNCIÓN DE ABANDONO:</strong></p>
                <p>Si han transcurrido seis (6) meses desde la fecha de recepción del equipo sin que el cliente lo haya retirado, haya cancelado los servicios o manifestado su voluntad de hacerlo, se presumirá el ABANDONO VOLUNTARIO DEL BIEN por parte del cliente, conforme a lo establecido en el Código Civil. En consecuencia, la empresa quedaría exonerada de toda responsabilidad sobre el bien depositado, pudiendo disponer de él, venderlo o enajenarlo, con el fin de recuperar los costos de almacenamiento y las sumas adeudadas.</p>
                <p><strong>NOTIFICACIÓN:</strong></p>
                <p>La empresa se compromete a notificar al cliente, mediante comunicación escrita enviada a la dirección física o electrónica registrada, con al menos quince (15) días de anticipación al cumplimiento del plazo de seis (6) meses, informando sobre el estado del equipo y los cargos acumulados.</p>
                <p>El cliente declara haber sido informado de manera clara y expresa sobre estas condiciones, y manifiesta su total conformidad con las mismas.</p>
              </div>
              <q-checkbox v-model="ingresoForm.legal_accepted" label="Acepto las condiciones legales" />
            </div>

            <div v-else-if="currentStage === 2" class="section-block">
              <div class="section-title">Revisión</div>
                        <div class="row q-col-gutter-md">
                          <div class="col-xs-12 col-sm-6"><q-input filled readonly v-model="revisionForm.order_number" label="Orden de trabajo" dense /></div>
                          <div class="col-xs-12 col-sm-6"><q-input filled v-model="revisionForm.revision_observaciones" label="Observaciones de revisión" dense /></div>
                        </div>
              <div class="section-title q-mt-md">Accesorios</div>
              <div class="accessories-grid revision-accessories-grid">
                <div class="accessory-header">Item</div>
                <div class="accessory-header">Ingreso</div>
                <div class="accessory-header">Cambio</div>
                <div class="accessory-header">Cantidad</div>
                <div class="accessory-header">Costo</div>
                <div class="accessory-header">Referencia</div>
                <div class="accessory-header">Precio</div>
                <template v-for="(row, idx) in revisionForm.accessories" :key="(row.name||'rev') + idx">
                  <div class="accessory-cell accessory-item">{{ row.name }}</div>
                  <div class="accessory-cell"><q-select dense filled v-model="row.ingreso" :options="yesNoOptions" emit-value map-options class="cell-input" /></div>
                  <div class="accessory-cell"><q-select dense filled v-model="row.cambio" :options="yesNoOptions" emit-value map-options class="cell-input" /></div>
                  <div class="accessory-cell"><q-input dense filled v-model.number="row.cantidad" type="number" min="1" class="cell-input" @update:model-value="val => updateAccessoryPrice(row)" /></div>
                  <div class="accessory-cell"><q-input dense filled v-model.number="row.costo" type="number" min="0" prefix="$" class="cell-input" @update:model-value="val => updateAccessoryPrice(row)" /></div>
                  <div class="accessory-cell">
                    <q-select
                      dense
                      filled
                      v-model="row.producto_uuid"
                      :options="inventarioOptions"
                      option-value="value"
                      option-label="label"
                      use-input
                      input-debounce="200"
                      map-options
                      emit-value
                      :option-filter="filterInventarioOption"
                      :disable="row.cambio !== 'SI'"
                      @update:model-value="val => onSelectProduct(row, val)"
                      class="cell-input"
                    />
                  </div>
                  <div class="accessory-cell"><q-input dense filled v-model.number="row.precio" type="number" min="0" prefix="$" class="cell-input" readonly /></div>
                </template>
              </div>
              <div class="section-title q-mt-md">Procedimiento mecánico</div>
              <div class="row q-col-gutter-md q-mt-md">
                <div class="col-xs-12 col-sm-6">
                  <q-select
                    filled
                    v-model="revisionForm.mecanico.procesos"
                    :options="procesosOptions"
                    label="Procesos"
                    multiple
                    emit-value
                    map-options
                    dense
                    clearable
                  />
                </div>
              </div>
              <div class="section-title q-mt-md">Pruebas de ingreso</div>
              <div class="table-wrapper">
                <div class="table-grid header-row">
                  <div>Prueba</div>
                  <div>Fase A</div>
                  <div>Fase B</div>
                  <div>Fase C</div>
                </div>
                <div v-for="item in testRows" :key="item.key" class="table-grid body-row">
                  <div>{{ item.label }}</div>
                  <q-input filled dense v-model="revisionForm.tests_ingreso[item.key].a" square class="table-cell" />
                  <q-input filled dense v-model="revisionForm.tests_ingreso[item.key].b" square class="table-cell" />
                  <q-input filled dense v-model="revisionForm.tests_ingreso[item.key].c" square class="table-cell" />
                </div>
              </div>
            </div>

            <div v-else-if="currentStage === 3" class="section-block">
              <div class="section-title">Procedimiento</div>
              <div class="row q-col-gutter-md">
                <div class="col-xs-12 col-sm-6"><q-input filled readonly v-model="procedimientoForm.order_number" label="Orden de trabajo" dense /></div>
                <div class="col-xs-12 col-sm-6"><q-input filled v-model="procedimientoForm.procedimiento_observaciones" label="Observaciones del procedimiento" dense /></div>
              </div>
              <div class="row q-col-gutter-md q-mt-md">
                <div class="col-xs-12 col-sm-6">
                  <q-select
                    filled
                    v-model="procedimientoForm.procesos"
                    :options="procesosOptions"
                    label="Procesos"
                    multiple
                    emit-value
                    map-options
                    dense
                    clearable
                  />
                </div>
              </div>
              <div class="section-title q-mt-md">Datos del bobinado</div>
              <div v-if="procedimientoHasRebobinado" class="q-mb-md">
                <template v-if="procedimientoTwoBobinado">
                  <div class="row q-col-gutter-md">
                    <div class="col-xs-12 col-sm-6">
                      <div class="text-subtitle2">Arranque</div>
                      <div class="row q-col-gutter-md">
                        <div class="col-xs-12 col-sm-6"><q-input filled v-model="procedimientoForm.bobinado.arranque.n_puntas" label="N° de puntas" dense /></div>
                        <div class="col-xs-12 col-sm-6"><q-input filled v-model="procedimientoForm.bobinado.arranque.conexion" label="Conexión" dense /></div>
                      </div>
                      <div class="row q-col-gutter-md q-mt-sm">
                        <div class="col-xs-12 col-sm-6"><q-input filled v-model="procedimientoForm.bobinado.arranque.n_grupos" label="N° Grupos" dense /></div>
                        <div class="col-xs-12 col-sm-6"><q-input filled v-model="procedimientoForm.bobinado.arranque.paso" label="Paso" dense /></div>
                      </div>
                    </div>
                    <div class="col-xs-12 col-sm-6">
                      <div class="text-subtitle2">Trabajo</div>
                      <div class="row q-col-gutter-md">
                        <div class="col-xs-12 col-sm-6"><q-input filled v-model="procedimientoForm.bobinado.trabajo.n_puntas" label="N° de puntas" dense /></div>
                        <div class="col-xs-12 col-sm-6"><q-input filled v-model="procedimientoForm.bobinado.trabajo.conexion" label="Conexión" dense /></div>
                      </div>
                      <div class="row q-col-gutter-md q-mt-sm">
                        <div class="col-xs-12 col-sm-6"><q-input filled v-model="procedimientoForm.bobinado.trabajo.n_grupos" label="N° Grupos" dense /></div>
                        <div class="col-xs-12 col-sm-6"><q-input filled v-model="procedimientoForm.bobinado.trabajo.paso" label="Paso" dense /></div>
                      </div>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <div class="row q-col-gutter-md">
                    <div class="col-xs-12 col-sm-3"><q-input filled v-model="procedimientoForm.bobinado.trabajo.n_puntas" label="N° de puntas" dense /></div>
                    <div class="col-xs-12 col-sm-3"><q-input filled v-model="procedimientoForm.bobinado.trabajo.conexion" label="Conexión de bobinado" dense /></div>
                    <div class="col-xs-12 col-sm-3"><q-input filled v-model="procedimientoForm.bobinado.trabajo.n_grupos" label="N° Grupos" dense /></div>
                    <div class="col-xs-12 col-sm-3"><q-input filled v-model="procedimientoForm.bobinado.trabajo.paso" label="Paso" dense /></div>
                  </div>
                </template>
              </div>
              <div class="section-title q-mt-md">Accesorios (procedimiento)</div>
              <div class="accessories-grid procedure-accessories-grid">
                <div class="accessory-header">Item</div>
                <div class="accessory-header">Cantidad</div>
                <div class="accessory-header">Costo</div>
                <div class="accessory-header">Referencia</div>
                <div class="accessory-header">Precio</div>
                <div class="accessory-header">Instalado</div>
                <template v-for="(row, idx) in procedimientoForm.accessories" :key="(row.name||'item') + idx">
                  <div class="accessory-cell accessory-item">{{ row.name }}</div>
                  <div class="accessory-cell"><q-input dense filled v-model.number="row.cantidad" type="number" min="0" class="cell-input" /></div>
                  <div class="accessory-cell"><q-input dense filled v-model.number="row.costo" type="number" min="0" prefix="$" class="cell-input" /></div>
                  <div class="accessory-cell">
                    <q-select
                      dense
                      filled
                      v-model="row.producto_uuid"
                      :options="inventarioOptions"
                      option-value="value"
                      option-label="label"
                      use-input
                      input-debounce="200"
                      map-options
                      emit-value
                      :option-filter="filterInventarioOption"
                      @update:model-value="val => onSelectProduct(row, val)"
                      class="cell-input"
                    />
                  </div>
                  <div class="accessory-cell"><q-input dense filled v-model.number="row.precio" type="number" min="0" prefix="$" class="cell-input" /></div>
                  <div class="accessory-cell"><q-checkbox dense v-model="row.instalado" /></div>
                </template>
              </div>

              <div class="section-title q-mt-md">Datos de construcción / modificaciones</div>
              <div class="row q-col-gutter-md">
                <div class="col-xs-12 col-sm-3"><q-input filled v-model="procedimientoForm.construccion.n_puntas" label="N° de puntas" dense /></div>
                <div class="col-xs-12 col-sm-3"><q-input filled v-model="procedimientoForm.construccion.conexion" label="Conexión de bobinado" dense /></div>
                <div class="col-xs-12 col-sm-3"><q-input filled v-model="procedimientoForm.construccion.n_grupos" label="N° Grupos" dense /></div>
                <div class="col-xs-12 col-sm-3"><q-input filled v-model="procedimientoForm.construccion.paso" label="Paso" dense /></div>
              </div>
              <div class="section-title q-mt-md">Peso por grupo</div>
              <div class="row q-col-gutter-md">
                <div class="col-xs-12 col-sm-4"><q-input filled v-model="procedimientoForm.peso_grupo.n1" label="N°1" dense /></div>
                <div class="col-xs-12 col-sm-4"><q-input filled v-model="procedimientoForm.peso_grupo.n6" label="N°6" dense /></div>
                <div class="col-xs-12 col-sm-4"><q-input filled v-model="procedimientoForm.peso_grupo.n12" label="N°12" dense /></div>
              </div>
              <div class="section-title q-mt-md">Pruebas de salida</div>
              <div class="table-wrapper">
                <div class="table-grid header-row">
                  <div>Prueba</div>
                  <div>Fase A</div>
                  <div>Fase B</div>
                  <div>Fase C</div>
                </div>
                <div v-for="item in testRows" :key="item.key" class="table-grid body-row">
                  <div>{{ item.label }}</div>
                  <q-input filled dense v-model="procedimientoForm.tests_salida[item.key].a" square class="table-cell" />
                  <q-input filled dense v-model="procedimientoForm.tests_salida[item.key].b" square class="table-cell" />
                  <q-input filled dense v-model="procedimientoForm.tests_salida[item.key].c" square class="table-cell" />
                </div>
              </div>
            </div>

            <div v-else class="section-block">
              <div class="section-title">Entrega</div>
              <div class="row q-col-gutter-md">
                <div class="col-xs-12 col-sm-6"><q-input filled readonly v-model="entregaForm.order_number" label="Orden de trabajo" dense /></div>
                <div class="col-xs-12 col-sm-6"><q-input filled v-model="entregaForm.fecha_entrega" label="Fecha de entrega" type="date" dense /></div>
              </div>
              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-12 col-sm-6"><q-input filled v-model="entregaForm.responsable" label="Responsable" dense /></div>
                <div class="col-xs-12 col-sm-6"><q-input filled v-model="entregaForm.estado" label="Estado de entrega" dense /></div>
              </div>
              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-12"><q-input filled v-model="entregaForm.observaciones" label="Observaciones" type="textarea" rows="3" dense /></div>
              </div>
              <div v-if="currentOrder" class="section-title q-mt-md">Resultados de pruebas de salida</div>
              <div v-if="currentOrder" class="table-wrapper">
                <div class="table-grid header-row">
                  <div>Prueba</div>
                  <div>Fase A</div>
                  <div>Fase B</div>
                  <div>Fase C</div>
                </div>
                <div v-for="item in testRows" :key="item.key" class="table-grid body-row">
                  <div>{{ item.label }}</div>
                  <div>{{ getOutputTestValue(currentOrder, item.key, 'a') }}</div>
                  <div>{{ getOutputTestValue(currentOrder, item.key, 'b') }}</div>
                  <div>{{ getOutputTestValue(currentOrder, item.key, 'c') }}</div>
                </div>
              </div>
            </div>

            <div class="row justify-end q-gutter-sm q-mt-md">
              <q-btn flat label="Cancelar" color="negative" @click="closeModal" />
              <q-btn unelevated label="Guardar etapa" color="primary" type="submit" />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { reactive, ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Notify, Dialog } from 'quasar'
import { api } from 'src/boot/axios'

const route = useRoute()

const currentStage = computed(() => route.meta?.stage || 1)

const stageLabel = computed(() => {
  const labels = { 1: 'Ingreso', 2: 'Revisión', 3: 'Procedimiento', 4: 'Entrega' }
  return labels[currentStage.value] || 'Ingreso'
})

const fasesOptions = [
  { label: 'Monofasico', value: 'Monofasico' },
  { label: 'Bifasico', value: 'Bifasico' },
  { label: 'Trifasico', value: 'Trifasico' },
  { label: 'Otros', value: 'Otros' }
]

const procesosOptions = [
  { label: 'Rebobinado', value: 'Rebobinado' },
  { label: 'Reconexion', value: 'Reconexion' },
  { label: 'Mantenimiento General', value: 'Mantenimiento General' }
]

const yesNoOptions = [
  { label: 'Sí', value: 'SI' },
  { label: 'No', value: 'NO' }
]
const stageDescription = computed(() => {
  const descriptions = {
    1: 'Registra nueva orden con datos de cliente y equipo.',
    2: 'Revisa accesorios, procedimiento mecánico y pruebas de ingreso.',
    3: 'Ejecuta procedimiento y pruebas de salida.',
    4: 'Entrega equipo y cierra orden.'
  }
  return descriptions[currentStage.value] || 'Gestión de órdenes'
})

const ingresos = ref([])
const clientes = ref([])
const inventario = ref([])
const inventarioOptions = computed(() => inventario.value.map(i => ({ label: `${i.codigo || ''} ${i.nombre || ''} (stock: ${i.cantidad || i.cantidad_disponible || i.stock || 0})`, value: i.uuid, raw: i })))
const selectedClientUuid = ref(null)
const showModal = ref(false)
const selectedOrderUuid = ref(null)
const pagination = ref({ page: 1, rowsPerPage: 10 })
const showClosedOrders = ref(false)

const motorOptions = [
  'Generador',
  'Motobomba',
  'Motobomba Sumergible',
  'Unidad de Refrigeracion',
  'Planta Electrica',
  'Maquina H',
  'Hidrolavadora',
  'Freno',
  'No Aplica',
  'Turbina',
  'Estator Generador',
  'Estator Motor',
  'Servomotor',
  'Estator Polipasto',
  'Polipasto',
  'Motovibrador',
  'Wincher',
  'Motoreductor',
  'Aireadores',
  'Motor Extractor'
]

const marcaOptions = [
  'Weg', 'Siemens', 'Baldor', 'Century', 'Chino', 'Honda', 'Vogues', 'ABB', 'A.O. Shmit', 'ATB', 'Barnes', 'Delcrosa', 'No Aplica', 'Vela STM', 'Gamak', 'Induccion Motor', 'Sin Placa', 'Perske', 'Sew', 'Nidec', 'Hyundai', 'Lesson', 'Robusto', 'Abus', 'Vibrator', 'Tech-Top', 'Nord', 'Newman', 'Irvime', 'Metal Corte', 'Intex', 'Maaax', 'Pearl', 'Ilegible', 'Aqua Park', 'Parva Lux', 'AC Sincrono', 'Copeland', 'Magnetec', 'Elle-Gi', 'Wide', 'Nova', 'ABM', 'Whirpool', 'Otros'
]

const columns = [
  { name: 'order_number', label: 'N° orden', field: 'order_number', align: 'left' },
  { name: 'fecha', label: 'Fecha', field: 'fecha', align: 'left' },
  { name: 'cliente', label: 'Cliente', field: 'cliente', align: 'left' },
  { name: 'motor', label: 'Motor', field: 'motor', align: 'left' },
  { name: 'servicio', label: 'Servicio', field: 'servicio', align: 'left' },
  { name: 'telefono', label: 'Teléfono', field: 'telefono', align: 'left' },
  { name: 'status', label: 'Estado', field: 'status', align: 'left' },
  { name: 'actions', label: 'Acciones', field: 'actions', align: 'center' }
]



const testRows = [
  { key: 'aislamiento', label: 'Aislamiento a Tierra' },
  { key: 'continuidad', label: 'Prueba de Continuidad' },
  { key: 'cortocircuito', label: 'Prueba de Cortocircuito' },
  { key: 'vacio', label: 'Corriente en Vacío' },
  { key: 'voltaje_prueba', label: 'Voltaje de Prueba' },
  { key: 'voltaje_operacion', label: 'Voltaje de Operación' }
]

function createIngresoForm () {
  return {
    order_number: '',
    fecha: '',
    cliente: '',
    contacto: '',
    telefono: '',
    motor: '',
    marca_choice: null,
    marca_custom: '',
    marca: '',
    serie: '',
    fases: '',
    modelo: '',
    peso: '',
    ip: '',
    aisl_cl: '',
    voltaje: '',
    corriente: '',
    la_in: '',
    cos: '',
    servicio: '',
    h2: '',
    conexion_placa: '',
    nro_puntas: '',
    legal_accepted: false,
    legal_notes: ''
  }
}

function createRevisionForm () {
  return {
    order_number: '',
    revision_observaciones: '',
    accessories: [
      { name: 'Rto de Accionamiento', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Rto de Ventilación', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Polea', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Caja Bornera', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Tapa Caja Bornera', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Bornera', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Ventilador', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Enfocador', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Tornillería', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Condensador Arranque', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Condensador Permanente', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Platino', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Centrífugo', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Caracola', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Impulsor', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Sello Mecánico', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Empaques', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Retenedores', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Aceite', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Cable', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Rebobinado', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Reconexión', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 },
      { name: 'Mtto General', ingreso: '', cambio: '', cantidad: 1, costo: 0, producto_uuid: null, referencia: '', precio: 0 }
    ],
    mecanico: {
      procesos: []
    },
    tests_ingreso: {
      aislamiento: { a: '', b: '', c: '' },
      continuidad: { a: '', b: '', c: '' },
      cortocircuito: { a: '', b: '', c: '' },
      vacio: { a: '', b: '', c: '' },
      voltaje_prueba: { a: '', b: '', c: '' },
      voltaje_operacion: { a: '', b: '', c: '' }
    }
  }
}

function createProcedimientoForm () {
  return {
    order_number: '',
    procedimiento_observaciones: '',
    procesos: [],
    accessories: [],
    bobinado: {
      arranque: {
        n_puntas: '',
        conexion: '',
        n_grupos: '',
        paso: '',
        awg: '',
        conexion_externa: '',
        sistema: '',
        bobinas_por_grupo: ''
      },
      trabajo: {
        n_puntas: '',
        conexion: '',
        n_grupos: '',
        paso: '',
        awg: '',
        conexion_externa: '',
        sistema: '',
        bobinas_por_grupo: ''
      }
    },
    construccion: {
      n_puntas: '',
      conexion: '',
      n_grupos: '',
      paso: '',
      awg: '',
      conexion_externa: '',
      sistema: '',
      bobinas_por_grupo: ''
    },
    peso_grupo: {
      n1: '',
      n3: '',
      n6: '',
      n9: '',
      n12: '',
      n15: '',
      n18: '',
      n21: '',
      n24: '',
      cable_salida: '',
      lh: '',
      di: '',
      ec: '',
      diente: '',
      ranuras: ''
    },
    tests_salida: {
      aislamiento: { a: '', b: '', c: '' },
      continuidad: { a: '', b: '', c: '' },
      cortocircuito: { a: '', b: '', c: '' },
      vacio: { a: '', b: '', c: '' },
      voltaje_prueba: { a: '', b: '', c: '' },
      voltaje_operacion: { a: '', b: '', c: '' }
    }
  }
}

function createEntregaForm () {
  return {
    order_number: '',
    fecha_entrega: '',
    responsable: '',
    estado: '',
    observaciones: ''
  }
}

const ingresoForm = reactive(createIngresoForm())
const revisionForm = reactive(createRevisionForm())
const procedimientoForm = reactive(createProcedimientoForm())
const entregaForm = reactive(createEntregaForm())

const currentOrder = computed(() => ingresos.value.find(item => item.uuid === selectedOrderUuid.value) || null)

const pendingOrders = computed(() => ingresos.value.filter(item => !item.status || item.status === 'ingreso'))
const revisionOrders = computed(() => ingresos.value.filter(item => item.status === 'revision'))
const procedimientoOrders = computed(() => ingresos.value.filter(item => item.status === 'procedimiento'))
const entregaOrders = computed(() => ingresos.value.filter(item => item.status === 'entrega' || item.status === 'cerrada'))
const closedOrders = computed(() => ingresos.value.filter(item => item.status === 'cerrada' || item.status === 'negada'))

const filteredIngresos = computed(() => {
  if (currentStage.value === 1) {
    return showClosedOrders.value ? closedOrders.value : pendingOrders.value
  }

  if (currentStage.value === 2) {
    return [...pendingOrders.value, ...revisionOrders.value]
  }

  if (currentStage.value === 3) {
    return [...revisionOrders.value, ...procedimientoOrders.value]
  }

  if (currentStage.value === 4) {
    return [...procedimientoOrders.value, ...entregaOrders.value]
  }

  return []
})

const currentStageLabel = computed(() => `Taller - ${stageLabel.value}`)
const currentOrderNumber = computed(() => {
  return currentOrder.value?.order_number || currentOrder.value?.ingreso?.order_number || ''
})
const currentOrderLabel = computed(() => {
  if (!currentOrder.value) {
    return currentStage.value === 1 ? 'Nuevo ingreso' : 'Selecciona una orden desde la tabla'
  }

  const clienteName = currentOrder.value.cliente?.nombre || currentOrder.value.ingreso?.cliente || currentOrder.value.ingreso?.cliente_uuid || 'Sin cliente'
  const orderNumber = currentOrderNumber.value || 'Sin orden'
  return `Orden ${orderNumber} · ${clienteName}`
})

const procedimientoHasRebobinado = computed(() => {
  return Array.isArray(procedimientoForm.procesos) && procedimientoForm.procesos.includes('Rebobinado')
})

const ingresoFases = computed(() => {
  return currentOrder.value?.ingreso?.fases || ''
})

const procedimientoTwoBobinado = computed(() => {
  return procedimientoHasRebobinado.value && ['Monofasico', 'Bifasico'].includes(ingresoFases.value)
})

function cloneValue (value) {
  return JSON.parse(JSON.stringify(value))
}

function hydrateForms (order = null) {
  const incomingOrder = order || null
  const ingresoData = incomingOrder?.ingreso || {}
  const revisionData = incomingOrder?.revision || {}
  const procedimientoData = incomingOrder?.procedimiento || {}
  const entregaData = incomingOrder?.entrega || {}

  Object.assign(ingresoForm, cloneValue(createIngresoForm()), cloneValue(ingresoData))
  ingresoForm.order_number = incomingOrder?.order_number || ingresoData.order_number || ingresoForm.order_number || ''
  ingresoForm.marca_choice = marcaOptions.includes(ingresoForm.marca) ? ingresoForm.marca : (ingresoForm.marca ? 'Otros' : null)
  ingresoForm.marca_custom = ingresoForm.marca_choice === 'Otros' ? ingresoForm.marca : ''
  selectedClientUuid.value = incomingOrder?.cliente_uuid || incomingOrder?.cliente?.uuid || null


  Object.assign(revisionForm, cloneValue(createRevisionForm()), cloneValue(revisionData))
  revisionForm.order_number = incomingOrder?.order_number || incomingOrder?.ingreso?.order_number || revisionData.order_number || revisionForm.order_number || ''
  revisionForm.accessories = cloneValue(revisionData.accessories || createRevisionForm().accessories)
  revisionForm.mecanico = { ...cloneValue(createRevisionForm().mecanico), ...(revisionData.mecanico || {}) }
  revisionForm.tests_ingreso = { ...cloneValue(createRevisionForm().tests_ingreso), ...(revisionData.tests_ingreso || {}) }

  Object.assign(procedimientoForm, cloneValue(createProcedimientoForm()), cloneValue(procedimientoData))
  procedimientoForm.order_number = incomingOrder?.order_number || incomingOrder?.ingreso?.order_number || procedimientoData.order_number || procedimientoForm.order_number || ''
  // Prefer saved procedimiento.procesos, otherwise inherit from revision selection
  procedimientoForm.procesos = procedimientoData.procesos || revisionData?.mecanico?.procesos || []
  // accessories: take from procedimiento if present, otherwise copy revision accessories and add instalado flag
  procedimientoForm.accessories = cloneValue(procedimientoData.accessories || (revisionData.accessories ? revisionData.accessories.filter(a => a.cambio === 'SI').map(a => ({ ...a, instalado: false })) : []))
  procedimientoForm.bobinado = {
    arranque: { ...cloneValue(createProcedimientoForm().bobinado.arranque), ...((procedimientoData.bobinado && procedimientoData.bobinado.arranque) || {}) },
    trabajo: { ...cloneValue(createProcedimientoForm().bobinado.trabajo), ...((procedimientoData.bobinado && procedimientoData.bobinado.trabajo) || {}) }
  }
  procedimientoForm.construccion = { ...cloneValue(createProcedimientoForm().construccion), ...(procedimientoData.construccion || {}) }
  procedimientoForm.peso_grupo = { ...cloneValue(createProcedimientoForm().peso_grupo), ...(procedimientoData.peso_grupo || {}) }
  procedimientoForm.tests_salida = { ...cloneValue(createProcedimientoForm().tests_salida), ...(procedimientoData.tests_salida || {}) }

  Object.assign(entregaForm, cloneValue(createEntregaForm()), cloneValue(entregaData))
  entregaForm.order_number = incomingOrder?.order_number || incomingOrder?.ingreso?.order_number || entregaData.order_number || entregaForm.order_number || ''
}

function filterInventarioOption (option, filter, label) {
  const query = String(filter || '').trim().toLowerCase()
  if (!query) {
    return true
  }

  const text = String(label || option.label || option.value || '').toLowerCase()
  return text.includes(query)
}

function openModal (row = null) {
  selectedOrderUuid.value = row?.uuid || null
  if (!row) {
    selectedClientUuid.value = null
  }
  hydrateForms(row)
  if (!row) {
    ingresoForm.order_number = generateOrderNumber()
  }
  showModal.value = true
}

function closeModal () {
  showModal.value = false
}

function generateUuid () {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return `uuid-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function generateOrderNumber () {
  const existingNumbers = ingresos.value
    .map(item => item.order_number)
    .filter(Boolean)
    .map(orderNumber => {
      const match = orderNumber.match(/^OT-(\d+)$/)
      return match ? Number(match[1]) : null
    })
    .filter(num => num !== null)

  const startingNumber = 10715
  const nextNumber = existingNumbers.length ? Math.max(...existingNumbers) + 1 : startingNumber
  return `OT-${nextNumber}`
}
function normalizeMarca () {
  if (ingresoForm.marca_choice === 'Otros') {
    ingresoForm.marca = ingresoForm.marca_custom || ''
  } else {
    ingresoForm.marca = ingresoForm.marca_choice || ''
  }
}

async function loadInventario() {
  try {
    const r = await api.get('core/inventario/')
    const data = r.data
    inventario.value = Array.isArray(data) ? data : (data?.results || [])
  } catch (err) {
    console.error('Error cargando inventario:', err)
    inventario.value = []
  }
}

function onSelectProduct(row, uuid) {
  row.producto_uuid = uuid
  const prod = inventario.value.find(i => i.uuid === uuid)
  if (prod) {
    row.referencia = prod.codigo || prod.nombre || ''
    row.costo = Number(prod.precio_unitario || prod.costo || 0)
  }
  updateAccessoryPrice(row)
}

function updateAccessoryPrice(row) {
  const cantidad = Number(row.cantidad || 0)
  const costo = Number(row.costo || 0)
  row.precio = Number((cantidad * costo).toFixed(2))
}

const accessoriesTotal = computed(() => {
  return revisionForm.accessories.reduce((s, r) => s + (Number(r.precio || 0)), 0)
})

function buildOrderPayload (order) {
  return {
    order_number: order.order_number,
    fecha: order.fecha,
    cliente_uuid: order.cliente_uuid || order.cliente?.uuid || selectedClientUuid.value || null,
    status: order.status,
    ingreso: order.ingreso || {},
    revision: order.revision || {},
    procedimiento: order.procedimiento || {},
    entrega: order.entrega || {}
  }
}

function buildNewIngresoOrder () {
  normalizeMarca()
  return {
    order_number: (ingresoForm.order_number || '').trim() || generateOrderNumber(),
    fecha: ingresoForm.fecha,
    cliente_uuid: selectedClientUuid.value || null,
    status: 'ingreso',
    ingreso: cloneValue(ingresoForm),
    revision: {},
    procedimiento: {},
    entrega: {}
  }
}

function submitStage () {
  if (currentStage.value === 1) {
    const existing = ingresos.value.find(item => item.uuid === selectedOrderUuid.value)
    const payload = buildNewIngresoOrder()

    if (existing) {
      const updatePayload = buildOrderPayload({
        ...existing,
        order_number: payload.order_number,
        fecha: payload.fecha,
        cliente_uuid: payload.cliente_uuid,
        ingreso: payload.ingreso,
        status: 'ingreso'
      })

      api.put(`core/taller/${existing.uuid}/`, updatePayload)
        .then(res => {
          const updated = res.data
          ingresos.value.splice(ingresos.value.findIndex(item => item.uuid === existing.uuid), 1, updated)
          selectedOrderUuid.value = updated.uuid
          Notify.create({ message: 'Ingreso actualizado', color: 'positive' })
          closeModal()
        })
        .catch(err => {
          console.error('Error actualizando ingreso:', err)
          Notify.create({ message: 'Error actualizando ingreso', color: 'negative' })
        })
    } else {
      const createPayload = buildNewIngresoOrder()
      api.post('core/taller/', createPayload)
        .then(res => {
          const created = res.data
          ingresos.value.unshift(created)
          selectedOrderUuid.value = created.uuid
          Notify.create({ message: 'Ingreso creado', color: 'positive' })
          closeModal()
        })
        .catch(err => {
          console.error('Error creando ingreso:', err)
          Notify.create({ message: 'Error creando ingreso', color: 'negative' })
        })
    }

    return
  }

  const selectedOrder = ingresos.value.find(item => item.uuid === selectedOrderUuid.value)
  if (!selectedOrder) {
    Notify.create({ message: 'Selecciona una orden para continuar', color: 'negative' })
    return
  }

  if (currentStage.value === 2) {
    selectedOrder.revision = cloneValue(revisionForm)
    selectedOrder.revision.order_number = selectedOrder.order_number
    selectedOrder.status = 'revision'
    const payload = buildOrderPayload(selectedOrder)
    api.put(`core/taller/${selectedOrder.uuid}/`, payload)
      .then(res => {
        const updated = res.data
        ingresos.value.splice(ingresos.value.findIndex(item => item.uuid === updated.uuid), 1, updated)
        Notify.create({ message: 'Revisión guardada', color: 'positive' })
      })
      .catch(err => {
        console.error('Error guardando revisión:', err)
        Notify.create({ message: 'Error guardando revisión', color: 'negative' })
      })
  } else if (currentStage.value === 3) {
    selectedOrder.procedimiento = cloneValue(procedimientoForm)
    selectedOrder.procedimiento.order_number = selectedOrder.order_number
    selectedOrder.status = 'procedimiento'
    const payload = buildOrderPayload(selectedOrder)
    api.put(`core/taller/${selectedOrder.uuid}/`, payload)
      .then(res => {
        const updated = res.data
        ingresos.value.splice(ingresos.value.findIndex(item => item.uuid === updated.uuid), 1, updated)
        Notify.create({ message: 'Procedimiento guardado', color: 'positive' })
      })
      .catch(err => {
        console.error('Error guardando procedimiento:', err)
        Notify.create({ message: 'Error guardando procedimiento', color: 'negative' })
      })
  } else if (currentStage.value === 4) {
    selectedOrder.entrega = {
      ...cloneValue(entregaForm),
      order_number: selectedOrder.order_number,
      output_tests: selectedOrder.procedimiento?.tests_salida || null
    }
    selectedOrder.status = 'cerrada'
    const payload = buildOrderPayload(selectedOrder)
    api.put(`core/taller/${selectedOrder.uuid}/`, payload)
      .then(res => {
        const updated = res.data
        ingresos.value.splice(ingresos.value.findIndex(item => item.uuid === updated.uuid), 1, updated)
        Notify.create({ message: 'Orden entregada y cerrada', color: 'positive' })
      })
      .catch(err => {
        console.error('Error guardando entrega:', err)
        Notify.create({ message: 'Error guardando entrega', color: 'negative' })
      })
  }

  closeModal()
}

function revertOrderStage (order) {
  if (!order) {
    return
  }

  if (order.status === 'revision') {
    order.status = 'ingreso'
    order.revision = {}
    Notify.create({ message: 'Orden devuelta a ingreso', color: 'warning' })
    return
  }

  if (order.status === 'procedimiento') {
    order.status = 'revision'
    order.procedimiento = {}
    Notify.create({ message: 'Orden devuelta a revisión', color: 'warning' })
    return
  }

  if (order.status === 'cerrada' || order.status === 'negada') {
    order.status = 'procedimiento'
    order.entrega = {}
    Notify.create({ message: 'Orden reabierta en procedimiento', color: 'warning' })
    return
  }

  ingresos.value = ingresos.value.filter(item => item.uuid !== order.uuid)
  Notify.create({ message: 'Ingreso eliminado', color: 'negative' })
}

function deleteIngreso (id) {
  const order = ingresos.value.find(item => item.uuid === id)
  if (!order) {
    return
  }
  if (order.status === 'procedimiento') {
    const revision = cloneValue(order.revision || {})
    const deletedProcedures = Array.isArray(revision.procedimientos_eliminados)
      ? revision.procedimientos_eliminados
      : []
    deletedProcedures.push({
      ...cloneValue(order.procedimiento || {}),
      eliminado_en: new Date().toISOString()
    })
    const revertedOrder = {
      ...order,
      status: 'revision',
      revision: { ...revision, procedimientos_eliminados: deletedProcedures },
      procedimiento: {}
    }
    api.put(`core/taller/${order.uuid}/`, buildOrderPayload(revertedOrder))
      .then(res => {
        const idx = ingresos.value.findIndex(item => item.uuid === order.uuid)
        if (idx !== -1) ingresos.value.splice(idx, 1, res.data)
        Notify.create({ message: 'Procedimiento eliminado y orden devuelta a revisión', color: 'warning' })
      })
      .catch(err => {
        console.error('Error devolviendo orden a revisión:', err)
        Notify.create({ message: 'Error devolviendo orden a revisión', color: 'negative' })
      })
    return
  }

  // Only remove an order permanently when it has not entered procedure.
  if (order && order.uuid) {
    api.delete(`core/taller/${order.uuid}/`)
      .then(() => {
        ingresos.value = ingresos.value.filter(item => item.uuid !== order.uuid)
        Notify.create({ message: 'Ingreso eliminado', color: 'negative' })
      })
      .catch(err => {
        console.error('Error eliminando ingreso:', err)
        Notify.create({ message: 'Error eliminando ingreso', color: 'negative' })
      })
  } else {
    revertOrderStage(order)
  }
}

const clienteOptions = computed(() => clientes.value.map(cliente => ({
  label: cliente.nombre || 'Cliente sin nombre',
  value: cliente.uuid || cliente.id
})))

const selectedClient = computed(() => clientes.value.find(cliente => cliente.uuid === selectedClientUuid.value || cliente.id === selectedClientUuid.value) || null)

watch(selectedClientUuid, (value) => {
  if (!value) return
  const cliente = selectedClient.value
  if (!cliente) return

  ingresoForm.cliente = cliente.nombre || ingresoForm.cliente
  ingresoForm.telefono = cliente.telefono || ingresoForm.telefono
  ingresoForm.contacto = cliente.contacto || cliente.correo || ingresoForm.contacto
})

function onMarcaSelect (value) {
  ingresoForm.marca_choice = value
  if (value !== 'Otros') {
    ingresoForm.marca = value
    ingresoForm.marca_custom = ''
  }
}

async function loadClientes () {
  try {
    const response = await api.get('core/cliente/')
    clientes.value = response.data || []
  } catch (error) {
    console.error('Error cargando clientes:', error)
    clientes.value = []
  }
}

async function loadIngresos() {
  try {
    const r = await api.get('core/taller/')
    ingresos.value = (r.data || []).map(item => {
      // Normalize incoming item to ensure table shows friendly values
      const cloned = { ...item }

      // ensure order_number at top-level
      const orderNumber = item.order_number || item.ingreso?.order_number || ''
      cloned.order_number = orderNumber

      // ensure fecha at top-level
      cloned.fecha = item.fecha || item.ingreso?.fecha || ''

      // ensure ingreso has order_number/fecha
      cloned.ingreso = { ...(item.ingreso || {}), order_number: item.ingreso?.order_number || orderNumber, fecha: item.ingreso?.fecha || cloned.fecha }

      // prefer cliente object when available, otherwise try to resolve by cliente_uuid
      if (!item.cliente && item.cliente_uuid && Array.isArray(clientes.value) && clientes.value.length) {
        const found = clientes.value.find(c => String(c.uuid) === String(item.cliente_uuid) || String(c.id) === String(item.cliente_uuid))
        cloned.cliente = found || null
      } else {
        cloned.cliente = item.cliente || null
      }

      return cloned
    })
  } catch (err) {
    console.error('Error cargando órdenes de taller:', err)
    ingresos.value = []
  }
}

onMounted(() => {
  loadClientes()
  loadInventario()
  loadIngresos()
})

function printIngreso () {
  normalizeMarca()
  const logoUrl = `${window.location.origin}/logo.png`
  const html = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>Orden de Ingreso ${ingresoForm.order_number}</title>
<style>
  body { margin: 0; padding: 0; font-family: Arial, sans-serif; color: #111827; }
  .page { width: 8.5in; min-height: 11in; padding: 0.75in; box-sizing: border-box; background: white; }
  .header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 18px; }
  .brand { font-size: 18px; font-weight: bold; margin-bottom: 6px; }
  .subtitle { font-size: 11px; margin: 2px 0; color: #4b5563; }
  .section { margin-bottom: 14px; }
  .section-title { font-size: 12px; font-weight: 700; margin-bottom: 8px; color: #111827; letter-spacing: 0.04em; }
  .row { display: flex; flex-wrap: wrap; gap: 12px; }
  .field { flex: 1 1 45%; min-width: 180px; }
  .label { font-size: 9px; color: #6b7280; margin-bottom: 3px; text-transform: uppercase; letter-spacing: 0.05em; }
  .value { font-size: 11px; font-weight: 600; color: #1f2937; }
  .box { border: 1px solid #d1d5db; border-radius: 8px; padding: 10px; background: #f8fafc; }
  .legal-note { font-size: 10px; color: #374151; line-height: 1.5; }
  .compact-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
  .full { flex: 1 1 100%; }
  .footer { font-size: 10px; color: #4b5563; margin-top: 16px; }
  @media print {
    body { margin: 0; }
    .page { box-shadow: none; }
    .page-break { page-break-before: always; }
  }
</style>
</head>
<body>
  <div class="page">
    <div class="header">
      <div style="display:flex; gap:12px; align-items:flex-start;">
        <img src="${logoUrl}" alt="Logo" style="width:72px; height:72px; object-fit:contain;" />
        <div>
          <div class="brand">BOBINADOS Y CONTROLES INDUSTRIALES</div>
          <div class="subtitle">Restrepo González & Asociados S.A.S</div>
          <div class="subtitle">NIT 902.012.726-2</div>
          <div class="subtitle">Calle 23 bis # 11-63 Pereira - R/da</div>
          <div class="subtitle">restrepoasociados2025@gmail.com • 311 360 5767 / 606 345 0838</div>
        </div>
      </div>
      <div style="text-align:right; min-width:180px;">
        <div class="section-title" style="margin-bottom:4px;">Orden de trabajo</div>
        <div class="value" style="font-size:24px;">${ingresoForm.order_number}</div>
        <div class="subtitle" style="margin-top:8px;">Fecha: ${ingresoForm.fecha || '-'}</div>
      </div>
    </div>
    <div class="section box">
      <div class="section-title">Datos del cliente</div>
      <div class="compact-grid">
        <div class="field"><div class="label">Cliente</div><div class="value">${ingresoForm.cliente || '-'}</div></div>
        <div class="field"><div class="label">Contacto</div><div class="value">${ingresoForm.contacto || '-'}</div></div>
        <div class="field"><div class="label">Teléfono</div><div class="value">${ingresoForm.telefono || '-'}</div></div>
        <div class="field"><div class="label">Orden</div><div class="value">${ingresoForm.order_number}</div></div>
      </div>
    </div>
    <div class="section box">
      <div class="section-title">Equipo</div>
      <div class="compact-grid">
        <div class="field"><div class="label">Motor</div><div class="value">${ingresoForm.motor || '-'}</div></div>
        <div class="field"><div class="label">Marca</div><div class="value">${ingresoForm.marca || '-'}</div></div>
        <div class="field"><div class="label">Serie</div><div class="value">${ingresoForm.serie || '-'}</div></div>
        <div class="field"><div class="label">Fases</div><div class="value">${ingresoForm.fases || '-'}</div></div>
        <div class="field"><div class="label">Modelo</div><div class="value">${ingresoForm.modelo || '-'}</div></div>
        <div class="field"><div class="label">Peso</div><div class="value">${ingresoForm.peso || '-'}</div></div>
        <div class="field"><div class="label">IP</div><div class="value">${ingresoForm.ip || '-'}</div></div>
        <div class="field"><div class="label">Aisl.Cl</div><div class="value">${ingresoForm.aisl_cl || '-'}</div></div>
        <div class="field"><div class="label">Voltaje</div><div class="value">${ingresoForm.voltaje || '-'}</div></div>
        <div class="field"><div class="label">Corriente</div><div class="value">${ingresoForm.corriente || '-'}</div></div>
        <div class="field"><div class="label">La/In</div><div class="value">${ingresoForm.la_in || '-'}</div></div>
        <div class="field"><div class="label">Cos</div><div class="value">${ingresoForm.cos || '-'}</div></div>
        <div class="field full"><div class="label">Servicio</div><div class="value">${ingresoForm.servicio || '-'}</div></div>
        <div class="field full"><div class="label">Conexión en placa</div><div class="value">${ingresoForm.conexion_placa || '-'}</div></div>
        <div class="field full"><div class="label">Nro de puntas</div><div class="value">${ingresoForm.nro_puntas || '-'}</div></div>
      </div>
    </div>
    <div class="footer">Documento generado para control interno de taller. Revisa los datos antes de la impresión final.</div>
  </div>
</body>
</html>`
  const printWindow = window.open('', '_blank')
  if (!printWindow) return
  printWindow.document.write(html)
  printWindow.document.close()
  printWindow.onload = () => {
    printWindow.focus()
    printWindow.print()
  }
}

function confirmAdvanceOrder (order) {
  if (!order) {
    Notify.create({ message: 'Orden inválida', color: 'negative' })
    return
  }

  Dialog.create({
    title: 'Avanzar orden',
    message: '¿Deseas avanzar esta orden a procedimiento o marcarla como negada?',
    cancel: 'Negado',
    persistent: true,
    ok: 'Avanzar a procedimiento'
  })
    .onOk(() => advanceToProcedimiento(order))
    .onCancel(() => denyOrder(order))
}

function advanceToProcedimiento (order) {
  if (!order) return
  // ensure procedimiento carries over selected procesos and accessories from revision
  const proc = order.procedimiento || {}
  proc.procesos = (order.revision && order.revision.mecanico && order.revision.mecanico.procesos) || proc.procesos || []
  if ((!proc.accessories || !proc.accessories.length) && order.revision && Array.isArray(order.revision.accessories)) {
    proc.accessories = order.revision.accessories
      .filter(a => a.cambio === 'SI')
      .map(a => ({ ...a, instalado: false }))
  }
  order.procedimiento = proc
  order.status = 'procedimiento'
  const payload = buildOrderPayload(order)
  api.put(`core/taller/${order.uuid}/`, payload)
    .then(res => {
      const updated = res.data
      const idx = ingresos.value.findIndex(i => i.uuid === updated.uuid)
      if (idx !== -1) ingresos.value.splice(idx, 1, updated)
      Notify.create({ message: 'Orden avanzada a procedimiento', color: 'positive' })
    })
    .catch(err => {
      console.error('Error avanzando orden:', err)
      Notify.create({ message: 'Error al avanzar orden', color: 'negative' })
    })
}

function denyOrder (order) {
  if (!order) return
  order.status = 'cerrada'
  order.entrega = {
    order_number: order.order_number,
    fecha_entrega: new Date().toISOString().slice(0, 10),
    responsable: 'NEGADO',
    estado: 'Negado',
    observaciones: 'Orden cerrada por negado en revisión'
  }
  const payload = buildOrderPayload(order)
  api.put(`core/taller/${order.uuid}/`, payload)
    .then(res => {
      const updated = res.data
      ingresos.value = ingresos.value.map(i => i.uuid === updated.uuid ? updated : i)
      Notify.create({ message: 'Orden marcada como negada y cerrada', color: 'negative' })
    })
    .catch(err => {
      console.error('Error marcando orden como negada:', err)
      Notify.create({ message: 'Error al marcar orden', color: 'negative' })
    })
}

function getOutputTestValue (order, testKey, phase) {
  return order?.procedimiento?.tests_salida?.[testKey]?.[phase] || '-'
}
</script>

<style scoped>
.taller-page {
  min-height: calc(100vh - 64px);
  background: #f7f9ff;
}

.taller-card {
  max-width: 1440px;
  margin: 0 auto;
  border-radius: 22px;
  overflow: hidden;
  box-shadow: 0 30px 80px rgba(15, 23, 42, 0.12);
}

.modal-card {
  width: min(98vw, 1700px);
  max-width: 98vw;
  min-height: 85vh;
  max-height: 98vh;
  overflow-y: auto;
  border-radius: 20px;
}

.section-block {
  padding: 20px 24px;
  background: #ffffff;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
}

.section-title {
  font-weight: 700;
  margin-bottom: 16px;
}

.table-wrapper {
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 14px;
  overflow: hidden;
}

.table-grid {
  display: grid;
  grid-template-columns: 2fr repeat(3, 1fr);
  gap: 12px;
  padding: 12px 16px;
}

.header-row {
  background: #eef3ff;
  font-weight: 700;
}

.body-row {
  background: #fff;
}

.table-cell {
  min-width: 0;
}

.accessories-grid {
  display: grid;
  gap: 0 10px;
  align-items: center;
  overflow-x: auto;
  padding: 0 8px 8px;
}

.revision-accessories-grid {
  grid-template-columns: minmax(210px, 2fr) repeat(6, minmax(110px, 1fr));
}

.procedure-accessories-grid {
  grid-template-columns: minmax(210px, 2fr) repeat(5, minmax(120px, 1fr));
}

.accessory-header {
  font-weight: 700;
  min-height: 52px;
  padding: 14px 10px;
  background: #fafbff;
  border-bottom: 1px solid rgba(15, 23, 42, 0.04);
  white-space: nowrap;
}

.accessory-cell {
  min-height: 58px;
  padding: 8px 10px;
  min-width: 0;
  display: flex;
  align-items: center;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
}

.accessory-item {
  font-weight: 600;
}

.cell-input :deep(.q-field__control) {
  min-height: 32px;
}

.legal-copy {
  font-size: 0.90rem;
  line-height: 1.65;
  color: #2f3a4a;
  background: #f9fafb;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.legal-copy strong {
  display: block;
  margin-bottom: 8px;
  margin-top: 8px;
  color: #102a43;
  font-size: 0.95rem;
}

.legal-copy p {
  margin: 0 0 8px;
}

.legal-copy p:first-child strong {
  margin-top: 0;
}
</style>
