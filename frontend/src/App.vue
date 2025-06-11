<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Zilla+Slab:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400;1,500;1,600;1,700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,300;1,400;1,500;1,600;1,700;1,800&display=swap');

body {
  font-family: 'Open Sans', sans-serif;
  color: #fff;
  line-height: 24px;
  font-size: 17px;
  font-weight: 300;
}

.gradient-body {
  background-image: linear-gradient(to right, #1f3f4d, #1d3d4d, #1b3b4e, #1a384e, #1a364e, #1c344f, #1f334f, #23314f, #293050, #2f2e50, #362c4f, #3c2a4e);
  background-color: #1e263b;
}

h1, h2, h3, h4, h5 {
  font-family: 'Zilla Slab', serif;
  color: #fff;
}

.btn {
  border: none;
  font-size: 14px;
  padding: 8px 16px;
  border-radius: 4px;
  transition: 0.3s;
}

.btn-grad-blue {
  background: linear-gradient(45deg, #6693fa, #6fb9e9);
  color: #fff;
}

.btn-grad-blue:hover {
  opacity: 0.9;
  color: #fff;
}

.btn-green {
  background-color: #24c2ab;
  color: #fff;
}

.btn-green:hover {
  opacity: 0.9;
  color: #fff;
}

.text-secondary {
  color: #b1bacd !important;
}

a {
  color: #24c2ab;
  text-decoration: none;
  transition: 0.3s;
}

a:hover {
  opacity: 0.8;
}

.form-control {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  font-size: 14px;
}

.form-control:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: #24c2ab;
  color: #fff;
  box-shadow: none;
}

.form-control::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  background: linear-gradient(to right, rgba(0, 128, 0, 0.1) 0%, rgba(128, 0, 128, 0.1) 100%);
}

#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
  background: linear-gradient(to right, rgba(0, 128, 0, 0.1) 0%, rgba(128, 0, 128, 0.1) 100%);
  margin: 0;
  padding: 0;
  color: rgba(0, 128, 0, 0.8);
}
</style> 