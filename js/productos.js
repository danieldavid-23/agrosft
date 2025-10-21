// Base de datos de productos agrícolas
let productos = JSON.parse(localStorage.getItem('productos')) || [
    {
        id: 1,
        nombre: "Aguacate Hass",
        precio: 8000,
        categoria: "frutas",
        descripcion: "Aguacate Hass fresco de la región de Medellín",
        imagen: "🥑",
        vendedorId: null,
        cantidad: 100,
        fechaRegistro: new Date().toISOString()
    },
    {
        id: 2,
        nombre: "Plátano Maduro",
        precio: 2500,
        categoria: "frutas",
        descripcion: "Plátano maduro ideal para cocinar",
        imagen: "🍌",
        vendedorId: null,
        cantidad: 200,
        fechaRegistro: new Date().toISOString()
    },
    {
        id: 3,
        nombre: "Tomate Chonto",
        precio: 3000,
        categoria: "verduras",
        descripcion: "Tomate chonto fresco y jugoso",
        imagen: "🍅",
        vendedorId: null,
        cantidad: 150,
        fechaRegistro: new Date().toISOString()
    },
    {
        id: 4,
        nombre: "Zanahoria",
        precio: 2000,
        categoria: "verduras",
        descripcion: "Zanahoria fresca y crujiente",
        imagen: "🥕",
        vendedorId: null,
        cantidad: 120,
        fechaRegistro: new Date().toISOString()
    },
    {
        id: 5,
        nombre: "Fríjol Cargamanto",
        precio: 5000,
        categoria: "granos",
        descripcion: "Fríjol cargamanto de excelente calidad",
        imagen: "🫘",
        vendedorId: null,
        cantidad: 80,
        fechaRegistro: new Date().toISOString()
    },
    {
        id: 6,
        nombre: "Papa Pastusa",
        precio: 2500,
        categoria: "tubérculos",
        descripcion: "Papa pastusa ideal para cocinar",
        imagen: "🥔",
        vendedorId: null,
        cantidad: 300,
        fechaRegistro: new Date().toISOString()
    },
    {
        id: 7,
        nombre: "Naranja Valencia",
        precio: 1500,
        categoria: "frutas",
        descripcion: "Naranja valencia jugosa y dulce",
        imagen: "🍊",
        vendedorId: null,
        cantidad: 180,
        fechaRegistro: new Date().toISOString()
    },
    {
        id: 8,
        nombre: "Cebolla Cabezona",
        precio: 2800,
        categoria: "verduras",
        descripcion: "Cebolla cabezona blanca",
        imagen: "🧅",
        vendedorId: null,
        cantidad: 90,
        fechaRegistro: new Date().toISOString()
    }
];

// Función para guardar productos en localStorage
function guardarProductos() {
    localStorage.setItem('productos', JSON.stringify(productos));
}

// Función para agregar un nuevo producto
function agregarProducto(nombre, precio, categoria, descripcion, imagen, cantidad) {
    const nuevoProducto = {
        id: Date.now(),
        nombre,
        precio: parseInt(precio),
        categoria,
        descripcion,
        imagen: imagen || '🌱',
        vendedorId: usuarioActual ? usuarioActual.id : null,
        cantidad: parseInt(cantidad),
        fechaRegistro: new Date().toISOString()
    };
    
    productos.push(nuevoProducto);
    guardarProductos();
    return nuevoProducto;
}

// Función para mostrar productos
function mostrarProductos(categoria = 'todos') {
    const listaProductos = document.getElementById('lista-productos');
    listaProductos.innerHTML = '';
    
    const productosFiltrados = categoria === 'todos' 
        ? productos 
        : productos.filter(producto => producto.categoria === categoria);
    
    // Ordenar productos: primero los del usuario actual, luego los demás
    productosFiltrados.sort((a, b) => {
        if (usuarioActual) {
            if (a.vendedorId === usuarioActual.id && b.vendedorId !== usuarioActual.id) return -1;
            if (a.vendedorId !== usuarioActual.id && b.vendedorId === usuarioActual.id) return 1;
        }
        return 0;
    });
    
    if (productosFiltrados.length === 0) {
        listaProductos.innerHTML = '<p class="no-productos">No hay productos en esta categoría</p>';
        return;
    }
    
    productosFiltrados.forEach(producto => {
        const productoElemento = document.createElement('div');
        productoElemento.classList.add('producto');
        
        // Marcar productos del usuario actual
        if (usuarioActual && producto.vendedorId === usuarioActual.id) {
            productoElemento.classList.add('producto-usuario');
        }
        
        productoElemento.innerHTML = `
            <div class="producto-img">${producto.imagen}</div>
            <div class="producto-info">
                <h3>${producto.nombre}</h3>
                <p class="producto-precio">$${producto.precio.toLocaleString()} por kg</p>
                <p class="producto-cantidad">Disponible: ${producto.cantidad} kg</p>
                <p class="producto-descripcion">${producto.descripcion}</p>
                ${producto.cantidad > 0 ? 
                    `<button class="btn agregar-carrito" data-id="${producto.id}">Agregar al Carrito</button>` :
                    `<button class="btn btn-disabled" disabled>Agotado</button>`
                }
            </div>
        `;
        listaProductos.appendChild(productoElemento);
    });
    
    // Agregar event listeners a los botones de agregar al carrito
    document.querySelectorAll('.agregar-carrito').forEach(boton => {
        boton.addEventListener('click', function() {
            const idProducto = parseInt(this.getAttribute('data-id'));
            agregarAlCarrito(idProducto);
        });
    });
}

// Función para inicializar los filtros
function inicializarFiltros() {
    document.querySelectorAll('.filtro-btn').forEach(boton => {
        boton.addEventListener('click', function() {
            // Remover clase active de todos los botones
            document.querySelectorAll('.filtro-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Agregar clase active al botón clickeado
            this.classList.add('active');
            
            // Filtrar productos
            const categoria = this.getAttribute('data-categoria');
            mostrarProductos(categoria);
        });
    });
}

// Inicializar la página de productos cuando se carga
document.addEventListener('DOMContentLoaded', function() {
    mostrarProductos();
    inicializarFiltros();
});