// Carrito de compras
let carrito = JSON.parse(localStorage.getItem('carrito')) || [];

// Función para agregar producto al carrito
function agregarAlCarrito(idProducto) {
    const producto = productos.find(p => p.id === idProducto);
    
    if (producto) {
        const productoEnCarrito = carrito.find(item => item.id === idProducto);
        
        if (productoEnCarrito) {
            productoEnCarrito.cantidad += 1;
        } else {
            carrito.push({
                ...producto,
                cantidad: 1
            });
        }
        
        actualizarCarrito();
        guardarCarritoEnLocalStorage();
        
        // Mostrar mensaje de confirmación
        mostrarMensaje(`${producto.nombre} agregado al carrito`);
    }
}

// Función para eliminar producto del carrito
function eliminarDelCarrito(idProducto) {
    carrito = carrito.filter(item => item.id !== idProducto);
    actualizarCarrito();
    guardarCarritoEnLocalStorage();
}

// Función para actualizar cantidad de producto en el carrito
function actualizarCantidad(idProducto, nuevaCantidad) {
    if (nuevaCantidad <= 0) {
        eliminarDelCarrito(idProducto);
        return;
    }
    
    const productoEnCarrito = carrito.find(item => item.id === idProducto);
    if (productoEnCarrito) {
        productoEnCarrito.cantidad = nuevaCantidad;
        actualizarCarrito();
        guardarCarritoEnLocalStorage();
    }
}

// Función para actualizar la visualización del carrito
function actualizarCarrito() {
    const contadorCarrito = document.getElementById('contador-carrito');
    const contenidoCarrito = document.getElementById('contenido-carrito');
    const totalPrecio = document.getElementById('total-precio');
    
    // Actualizar contador
    const totalItems = carrito.reduce((total, item) => total + item.cantidad, 0);
    contadorCarrito.textContent = totalItems;
    
    // Actualizar contenido del carrito
    contenidoCarrito.innerHTML = '';
    
    if (carrito.length === 0) {
        contenidoCarrito.innerHTML = '<p>Tu carrito está vacío</p>';
        totalPrecio.textContent = '0';
        return;
    }
    
    let total = 0;
    
    carrito.forEach(item => {
        const subtotal = item.precio * item.cantidad;
        total += subtotal;
        
        const itemElemento = document.createElement('div');
        itemElemento.classList.add('item-carrito');
        itemElemento.innerHTML = `
            <div class="item-carrito-info">
                <h4>${item.nombre}</h4>
                <p>$${item.precio.toLocaleString()} x kg</p>
            </div>
            <div class="item-carrito-cantidad">
                <button class="disminuir" data-id="${item.id}">-</button>
                <span>${item.cantidad} kg</span>
                <button class="aumentar" data-id="${item.id}">+</button>
            </div>
            <div class="item-carrito-subtotal">
                $${subtotal.toLocaleString()}
            </div>
            <div class="eliminar-item" data-id="${item.id}">🗑️</div>
        `;
        contenidoCarrito.appendChild(itemElemento);
    });
    
    // Actualizar total
    totalPrecio.textContent = total.toLocaleString();
    
    // Agregar event listeners a los botones del carrito
    document.querySelectorAll('.disminuir').forEach(boton => {
        boton.addEventListener('click', function() {
            const idProducto = parseInt(this.getAttribute('data-id'));
            const item = carrito.find(item => item.id === idProducto);
            if (item) {
                actualizarCantidad(idProducto, item.cantidad - 1);
            }
        });
    });
    
    document.querySelectorAll('.aumentar').forEach(boton => {
        boton.addEventListener('click', function() {
            const idProducto = parseInt(this.getAttribute('data-id'));
            const item = carrito.find(item => item.id === idProducto);
            if (item) {
                actualizarCantidad(idProducto, item.cantidad + 1);
            }
        });
    });
    
    document.querySelectorAll('.eliminar-item').forEach(boton => {
        boton.addEventListener('click', function() {
            const idProducto = parseInt(this.getAttribute('data-id'));
            eliminarDelCarrito(idProducto);
        });
    });
}

// Función para guardar carrito en localStorage
function guardarCarritoEnLocalStorage() {
    localStorage.setItem('carrito', JSON.stringify(carrito));
}

// Función para mostrar mensajes
function mostrarMensaje(mensaje) {
    // Crear elemento de mensaje
    const mensajeElemento = document.createElement('div');
    mensajeElemento.textContent = mensaje;
    mensajeElemento.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: #2ecc71;
        color: white;
        padding: 15px 20px;
        border-radius: 5px;
        z-index: 3000;
        animation: slideIn 0.5s, slideOut 0.5s 2.5s;
    `;
    
    // Agregar estilos de animación
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(mensajeElemento);
    
    // Eliminar mensaje después de 3 segundos
    setTimeout(() => {
        document.body.removeChild(mensajeElemento);
    }, 3000);
}

// Función para finalizar compra
function finalizarCompra() {
    if (carrito.length === 0) {
        alert('Tu carrito está vacío');
        return;
    }
    
    // Simular proceso de compra
    alert('¡Gracias por tu compra! Te contactaremos para coordinar la entrega.');
    
    // Limpiar carrito
    carrito = [];
    actualizarCarrito();
    guardarCarritoEnLocalStorage();
    
    // Cerrar modal
    document.getElementById('modal-carrito').style.display = 'none';
}

// Inicializar carrito cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    actualizarCarrito();
});