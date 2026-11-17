<template>
  <h1>Объявления об аренде</h1>

  <div v-if="current">
    <p><button type="button" @click="current = null">К списку</button></p>
    <h2>{{ current.title || "Без названия" }}</h2>
    <p v-if="current.price != null">Цена: {{ current.price }} руб.</p>
    <p v-if="current.district">Район: {{ current.district }}</p>
    <p v-if="current.rooms != null">Комнат: {{ current.rooms }}</p>
    <p v-if="current.area != null">Площадь: {{ current.area }} м²</p>
    <p v-if="current.description">{{ current.description }}</p>
    <p v-for="src in current.photos" :key="src">
      <img :src="src" alt="">
    </p>
    <p>
      <button type="button" @click="toggleFavorite(current.id)">
        {{ isFavorite(current.id) ? "Убрать из избранного" : "В избранное" }}
      </button>
    </p>
  </div>

  <div v-else>
    <p>
      <input v-model="query" placeholder="Поиск по названию">
    </p>
    <p>
      Цена от <input v-model="priceFrom" type="number">
      до <input v-model="priceTo" type="number">
    </p>
    <p>
      Комнат
      <select v-model="rooms">
        <option value="">все</option>
        <option v-for="n in roomOptions" :key="n" :value="String(n)">{{ n }}</option>
      </select>
    </p>
    <p>
      Район
      <select v-model="district">
        <option value="">все</option>
        <option v-for="name in districts" :key="name" :value="name">{{ name }}</option>
      </select>
    </p>
    <p>
      <label>
        <input type="checkbox" v-model="onlyFavorites">
        только избранное
      </label>
    </p>
    <p>Найдено: {{ filtered.length }}</p>
    <p v-if="filtered.length === 0">По выбранным условиям объявления не найдены.</p>

    <div v-for="item in filtered" :key="item.id">
      <h2>{{ item.title || "Без названия" }}</h2>
      <p v-if="item.price != null">Цена: {{ item.price }} руб.</p>
      <p v-if="item.district">Район: {{ item.district }}</p>
      <p v-if="item.rooms != null">Комнат: {{ item.rooms }}</p>
      <p v-if="item.area != null">Площадь: {{ item.area }} м²</p>
      <p v-if="item.description">{{ item.description }}</p>
      <p v-for="src in item.photos" :key="src">
        <img :src="src" alt="">
      </p>
      <p>
        <button type="button" @click="current = item">Подробнее</button>
        <button type="button" @click="toggleFavorite(item.id)">
          {{ isFavorite(item.id) ? "Убрать из избранного" : "В избранное" }}
        </button>
      </p>
      <hr>
    </div>
  </div>
</template>

<script>
import listings from "./listings.js"

export default {
  data() {
    return {
      listings,
      query: "",
      priceFrom: "",
      priceTo: "",
      rooms: "",
      district: "",
      onlyFavorites: false,
      favoriteIds: JSON.parse(localStorage.getItem("favorites") || "[]"),
      current: null
    }
  },
  computed: {
    districts() {
      const names = this.listings.map((item) => item.district).filter(Boolean)
      return [...new Set(names)].sort()
    },
    roomOptions() {
      const values = this.listings.map((item) => item.rooms).filter((n) => n != null)
      return [...new Set(values)].sort((a, b) => a - b)
    },
    filtered() {
      const query = this.query.trim().toLowerCase()
      const from = this.priceFrom === "" ? null : Number(this.priceFrom)
      const to = this.priceTo === "" ? null : Number(this.priceTo)
      return this.listings.filter((item) => {
        if (query && !(item.title || "").toLowerCase().includes(query)) return false
        if (from != null && (item.price == null || item.price < from)) return false
        if (to != null && (item.price == null || item.price > to)) return false
        if (this.rooms !== "" && item.rooms !== Number(this.rooms)) return false
        if (this.district && item.district !== this.district) return false
        if (this.onlyFavorites && !this.favoriteIds.includes(item.id)) return false
        return true
      })
    }
  },
  methods: {
    isFavorite(id) {
      return this.favoriteIds.includes(id)
    },
    toggleFavorite(id) {
      if (this.isFavorite(id)) {
        this.favoriteIds = this.favoriteIds.filter((item) => item !== id)
      } else {
        this.favoriteIds = this.favoriteIds.concat(id)
      }
      localStorage.setItem("favorites", JSON.stringify(this.favoriteIds))
    }
  }
}
</script>
