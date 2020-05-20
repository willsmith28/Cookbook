<template>
  <md-chips v-model="tags" md-static />
</template>

<script>
import { mapGetters } from "vuex";
export default {
  props: {
    tagIds: { type: Array, required: true }
  },
  computed: {
    tags() {
      return this.tagIds.map(tag_id => {
        const tag = this.getTag(tag_id);
        return `${tag.kind}: ${tag.value}`;
      });
    },
    ...mapGetters("recipe", ["getTag"])
  }
};
</script>
