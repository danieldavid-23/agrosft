// Sistema de autenticación
let usuarios = JSON.parse(localStorage.getItem('usuarios')) || [];
let usuarioActual = JSON.parse(localStorage.getItem('usuarioActual')) || null;

// Función para registrar usuario
function registrarUsuario(nombre, email, password, tipo) {
    // Verificar si el usuario ya existe
    if (usuarios.find(u => u.email === email)) {
        return { exito: false, mensaje: 'El email ya está registrado' };
    }
    
    // Crear nuevo usuario
    const nuevoUsuario = {
        id: Date.now(),
        nombre,
        email,
        password, // En una aplicación real, esto debería estar encriptado
        tipo,
        fechaRegistro: new Date().toISOString()
    };
    
    usuarios.push(nuevoUsuario);
    localStorage.setItem('usuarios', JSON.stringify(usuarios));
    
    return { exito: true, mensaje: 'Usuario registrado exitosamente' };
}

// Función para iniciar sesión
function iniciarSesion(email, password) {
    const usuario = usuarios.find(u => u.email === email && u.password === password);
    
    if (usuario) {
        usuarioActual = usuario;
        localStorage.setItem('usuarioActual', JSON.stringify(usuarioActual));
        return { exito: true, mensaje: 'Inicio de sesión exitoso', usuario };
    } else {
        return { exito: false, mensaje: 'Email o contraseña incorrectos' };
    }
}

// Función para cerrar sesión
function cerrarSesion() {
    usuarioActual = null;
    localStorage.removeItem('usuarioActual');
    actualizarInterfazUsuario();
}

// Función para actualizar la interfaz según el estado de autenticación
function actualizarInterfazUsuario() {
    const btnLogin = document.getElementById('btn-login');
    const btnRegister = document.getElementById('btn-register');
    const userInfo = document.getElementById('user-info');
    const userName = document.getElementById('user-name');
    
    if (usuarioActual) {
        btnLogin.style.display = 'none';
        btnRegister.style.display = 'none';
        userInfo.style.display = 'flex';
        userName.textContent = usuarioActual.nombre;
        
        // Mostrar u ocultar botón de agregar producto según el tipo de usuario
        const btnAgregarProducto = document.getElementById('btn-agregar-producto');
        if (usuarioActual.tipo === 'vendedor') {
            btnAgregarProducto.style.display = 'inline-block';
        } else {
            btnAgregarProducto.style.display = 'none';
        }
    } else {
        btnLogin.style.display = 'inline-block';
        btnRegister.style.display = 'inline-block';
        userInfo.style.display = 'none';
    }
}

// Función para verificar si hay un usuario autenticado al cargar la página
function verificarAutenticacion() {
    if (usuarioActual) {
        actualizarInterfazUsuario();
    }
}

// Inicializar cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    verificarAutenticacion();
});