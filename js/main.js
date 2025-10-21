// Funcionalidades principales de la página
document.addEventListener('DOMContentLoaded', function() {
    // Navegación suave
    document.querySelectorAll('nav a').forEach(enlace => {
        enlace.addEventListener('click', function(e) {
            e.preventDefault();
            const destino = document.querySelector(this.getAttribute('href'));
            if (destino) {
                destino.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Modal del carrito
    const btnCarrito = document.getElementById('btn-carrito');
    const modalCarrito = document.getElementById('modal-carrito');
    const cerrarCarrito = modalCarrito.querySelector('.cerrar');
    
    btnCarrito.addEventListener('click', function() {
        modalCarrito.style.display = 'block';
    });
    
    cerrarCarrito.addEventListener('click', function() {
        modalCarrito.style.display = 'none';
    });
    
    // Modales
    const modales = [
        { id: 'modal-login', btn: 'btn-login' },
        { id: 'modal-registro-usuario', btn: 'btn-register' },
        { id: 'modal-registro', btn: 'btn-registro-vendedor' },
        { id: 'modal-agregar-producto', btn: 'btn-agregar-producto' }
    ];
    
    modales.forEach(modalInfo => {
        const modal = document.getElementById(modalInfo.id);
        const btn = document.getElementById(modalInfo.btn);
        const cerrar = modal.querySelector('.cerrar');
        
        if (btn) {
            btn.addEventListener('click', function() {
                modal.style.display = 'block';
            });
        }
        
        cerrar.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    });
    
    // Cerrar modal al hacer clic fuera
    window.addEventListener('click', function(e) {
        modales.forEach(modalInfo => {
            const modal = document.getElementById(modalInfo.id);
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // Formulario de registro de usuario
    const formularioRegistroUsuario = document.getElementById('formulario-registro-usuario');
    formularioRegistroUsuario.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const nombre = document.getElementById('registro-nombre').value;
        const email = document.getElementById('registro-email').value;
        const password = document.getElementById('registro-password').value;
        const confirmar = document.getElementById('registro-confirmar').value;
        const tipo = document.getElementById('registro-tipo').value;
        
        if (password !== confirmar) {
            alert('Las contraseñas no coinciden');
            return;
        }
        
        const resultado = registrarUsuario(nombre, email, password, tipo);
        
        if (resultado.exito) {
            alert(resultado.mensaje);
            document.getElementById('modal-registro-usuario').style.display = 'none';
            formularioRegistroUsuario.reset();
            
            // Iniciar sesión automáticamente después del registro
            const inicioSesion = iniciarSesion(email, password);
            if (inicioSesion.exito) {
                actualizarInterfazUsuario();
                mostrarProductos(); // Actualizar lista de productos
            }
        } else {
            alert(resultado.mensaje);
        }
    });
    
    // Formulario de inicio de sesión
    const formularioLogin = document.getElementById('formulario-login');
    formularioLogin.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        
        const resultado = iniciarSesion(email, password);
        
        if (resultado.exito) {
            alert(resultado.mensaje);
            document.getElementById('modal-login').style.display = 'none';
            formularioLogin.reset();
            actualizarInterfazUsuario();
            mostrarProductos(); // Actualizar lista de productos
        } else {
            alert(resultado.mensaje);
        }
    });
    
    // Formulario de agregar producto
    const formularioAgregarProducto = document.getElementById('formulario-agregar-producto');
    formularioAgregarProducto.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!usuarioActual) {
            alert('Debes iniciar sesión para agregar productos');
            return;
        }
        
        const nombre = document.getElementById('producto-nombre').value;
        const precio = document.getElementById('producto-precio').value;
        const categoria = document.getElementById('producto-categoria').value;
        const descripcion = document.getElementById('producto-descripcion').value;
        const imagen = document.getElementById('producto-imagen').value;
        const cantidad = document.getElementById('producto-cantidad').value;
        
        const nuevoProducto = agregarProducto(nombre, precio, categoria, descripcion, imagen, cantidad);
        
        alert(`Producto "${nuevoProducto.nombre}" agregado exitosamente`);
        document.getElementById('modal-agregar-producto').style.display = 'none';
        formularioAgregarProducto.reset();
        
        // Actualizar lista de productos
        const filtroActivo = document.querySelector('.filtro-btn.active');
        const categoriaFiltro = filtroActivo ? filtroActivo.getAttribute('data-categoria') : 'todos';
        mostrarProductos(categoriaFiltro);
    });
    
    // Enlaces entre modales de login y registro
    document.getElementById('link-registro').addEventListener('click', function(e) {
        e.preventDefault();
        document.getElementById('modal-login').style.display = 'none';
        document.getElementById('modal-registro-usuario').style.display = 'block';
    });
    
    document.getElementById('link-login').addEventListener('click', function(e) {
        e.preventDefault();
        document.getElementById('modal-registro-usuario').style.display = 'none';
        document.getElementById('modal-login').style.display = 'block';
    });
    
    // Cerrar sesión
    document.getElementById('btn-logout').addEventListener('click', function() {
        cerrarSesion();
        mostrarProductos(); // Actualizar lista de productos
        alert('Sesión cerrada exitosamente');
    });
    
    // Formulario de contacto
    const formularioContacto = document.querySelector('.formulario-contacto');
    formularioContacto.addEventListener('submit', function(e) {
        e.preventDefault();
        alert('¡Mensaje enviado! Te responderemos pronto.');
        formularioContacto.reset();
    });
    
    // Botón finalizar compra
    const btnFinalizarCompra = document.getElementById('btn-finalizar-compra');
    btnFinalizarCompra.addEventListener('click', finalizarCompra);
    
    // Actualizar año en el footer
    const añoActual = new Date().getFullYear();
    document.querySelector('.footer-bottom p').innerHTML = `&copy; ${añoActual} AgroMarket Medellín. Todos los derechos reservados.`;
});// Efecto de scroll en el header
window.addEventListener('scroll', function() {
    const header = document.querySelector('header');
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});