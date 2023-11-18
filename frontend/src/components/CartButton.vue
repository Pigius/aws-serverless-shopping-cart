<template>
  <v-btn fixed right rounded small text icon x-large @click.stop="toggleDrawer">
    <v-icon color="black" x-large>mdi-cart</v-icon>
  </v-btn>
</template>

<script>
export default {
  name: "cart-button",
  methods: {
    toggleDrawer() {
      this.$emit("drawerChange");
    }
  }
};
</script>
<style scoped>
@-webkit-keyframes pulse {
  from {
    -webkit-transform: scale3d(1, 1, 1);
    transform: scale3d(1, 1, 1);
  }

  50% {
    -webkit-transform: scale3d(1.25, 1.25, 1.25);
    transform: scale3d(1.25, 1.25, 1.25);
  }

  to {
    -webkit-transform: scale3d(1, 1, 1);
    transform: scale3d(1, 1, 1);
  }
}

@keyframes pulse {
  from {
    -webkit-transform: scale3d(1, 1, 1);
    transform: scale3d(1, 1, 1);
  }

  50% {
    -webkit-transform: scale3d(1.25, 1.25, 1.25);
    transform: scale3d(1.25, 1.25, 1.25);
  }

  to {
    -webkit-transform: scale3d(1, 1, 1);
    transform: scale3d(1, 1, 1);
  }
}

.animated-pulse {
  animation: pulse 0.5s infinite;
}
</style>