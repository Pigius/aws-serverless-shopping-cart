<template>
  <v-card outlined class="flexcard" height="100%">
    <v-row class="pb-0" dense>
      <v-col :cols="8" class="mb-5">
        <v-card-title primary-title class="pb-0 pt-2">
          <p class="subtitle-2">{{product.name}}</p>
        </v-card-title>
      </v-col>
      <v-col>
        <p class="text-truncate body-2 pt-2 pb-0 pr-2 grow text-right mb-1">{{product.category}}</p>
      </v-col>
    </v-row>
    <v-card-text class="pt-0 pl-4 pb-0">
      <p class="pt-0 pb-0 mb-0 body-2">"{{product.description}}"</p>
      <p class="pt-0 pb-0 mb-0 body-2">"{{product.publisher}}"</p>
      <p class="price pt-0 pb-0 grow accent--text mb-1">${{getPrice(product)}}</p>
    </v-card-text>
  </v-card>
</template>

<script>
import { Decimal } from "decimal.js";

export default {
  props: ["product"],
  name: "product",
  methods: {
    getPrice(product) {
      return new Decimal(product.price/100).toFixed(2);
    }
  }
};
</script>

<style scoped>
.flexcard {
  position: relative;
  padding-bottom: 50px;
}
</style>
