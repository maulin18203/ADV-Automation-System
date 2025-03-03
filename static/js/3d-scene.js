let scene, camera, renderer, cube

function init() {
  // Create scene
  scene = new THREE.Scene()

  // Create camera
  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
  camera.position.z = 5

  // Create renderer
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(window.innerWidth, window.innerHeight)
  document.getElementById("scene-container").appendChild(renderer.domElement)

  // Create cube
  const geometry = new THREE.BoxGeometry(1, 1, 1)
  const material = new THREE.MeshPhongMaterial({ color: 0x00ff00 })
  cube = new THREE.Mesh(geometry, material)
  scene.add(cube)

  // Add lights
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
  scene.add(ambientLight)

  const pointLight = new THREE.PointLight(0xffffff, 1)
  pointLight.position.set(5, 5, 5)
  scene.add(pointLight)

  // Handle window resize
  window.addEventListener("resize", onWindowResize, false)

  // Start animation loop
  animate()
}

function animate() {
  requestAnimationFrame(animate)

  cube.rotation.x += 0.01
  cube.rotation.y += 0.01

  renderer.render(scene, camera)
}

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
}

// Initialize the 3D scene
init()

