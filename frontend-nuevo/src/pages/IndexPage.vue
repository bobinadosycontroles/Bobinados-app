<template>
  <q-page class="page-construction q-pa-lg column items-center justify-center">
    <div class="construction-card">
      <div class="hero-badge">
        <q-icon name="auto_awesome" size="22px" />
        <span>Experiencia digital en evolución</span>
      </div>

      <div class="text-h3 q-mt-md text-weight-bold">Tu sistema, más inteligente y visual</div>
      <div class="text-subtitle1 text-grey-7 q-mt-sm">
        Estamos refinando la experiencia para que cada módulo sea más claro, rápido y agradable de usar.
      </div>

      <div class="feature-grid q-mt-xl">
        <q-card flat bordered class="feature-card">
          <q-card-section class="column items-center text-center">
            <q-icon name="speed" size="34px" color="primary" />
            <div class="text-subtitle1 q-mt-sm">Rendimiento</div>
            <div class="text-caption text-grey-7">Flujos más ágiles y una navegación más fluida.</div>
          </q-card-section>
        </q-card>

        <q-card flat bordered class="feature-card">
          <q-card-section class="column items-center text-center">
            <q-icon name="palette" size="34px" color="deep-orange" />
            <div class="text-subtitle1 q-mt-sm">Diseño moderno</div>
            <div class="text-caption text-grey-7">Una interfaz fresca, limpia y preparada para crecer.</div>
          </q-card-section>
        </q-card>

        <q-card flat bordered class="feature-card">
          <q-card-section class="column items-center text-center">
            <q-icon name="hub" size="34px" color="teal" />
            <div class="text-subtitle1 q-mt-sm">Integración</div>
            <div class="text-caption text-grey-7">Más módulos, más conexiones y mejor experiencia global.</div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
</script>

<style scoped>
.page-construction {
  min-height: calc(100vh - 64px);
  background:
    radial-gradient(circle at top left, rgba(29, 78, 216, 0.12), transparent 28%),
    linear-gradient(135deg, #f8fbff 0%, #f3f7ff 60%, #eef3ff 100%);
}

.construction-card {
  width: min(100%, 860px);
  padding: 2.2rem;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 25px 80px rgba(15, 23, 42, 0.12);
  border: 1px solid rgba(63, 81, 181, 0.08);
  backdrop-filter: blur(10px);
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(29, 78, 216, 0.12), rgba(255, 138, 0, 0.12));
  color: #1e3a8a;
  font-weight: 600;
  font-size: 0.95rem;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.feature-card {
  border-radius: 18px;
  min-height: 180px;
  transition: transform 220ms ease, box-shadow 220ms ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
}

@media (max-width: 768px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }
}
</style>
