<template>
  <div>
    <input
      type="text"
      v-if="edit"
      class="cart-quantity-input text-center"
      v-model.trim="quantity"
      @focus="oldQuantity = $event.target.value, $event.target.select()"
      @blur="edit = false"
      @keyup.enter="$event.target.blur()"
      v-focus
    />
    <div
      @click="edit = true;"
      v-else
      class="pl-2 pr-2 noselect"
    >{{ quantity }}</div>
  </div>
</template>

<script>
export default {
  props: ["value"],

  data() {
    return {
      edit: false,
      quantity: this.value,
      oldQuantity: null
    };
  },
  watch: {
    value: function(newVal) {
      this.quantity = newVal;
    }
  },
  directives: {
    focus: {
      inserted(el) {
        el.focus();
      }
    }
  }
};
</script>

<style scoped>
.cart-quantity-input {
  width: 25px;
}
.noselect {
  -webkit-touch-callout: none; /* iOS Safari */
  -webkit-user-select: none; /* Safari */
  -khtml-user-select: none; /* Konqueror HTML */
  -moz-user-select: none; /* Old versions of Firefox */
  -ms-user-select: none; /* Internet Explorer/Edge */
  user-select: none; /* Non-prefixed version, currently
                                  supported by Chrome, Opera and Firefox */
}
.input-error {
  color: red;
}
</style>