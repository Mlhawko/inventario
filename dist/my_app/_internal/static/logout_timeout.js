
        // Función para redirigir al usuario al login
        function redirectLogin() {
            window.location.href = "/login";
        }

        // Reiniciar el temporizador cada vez que el usuario interactúa con la página
        function resetTimer() {
            clearTimeout(redirectTimer);
            redirectTimer = setTimeout(redirectLogin, 300000); // 30 segundos en milisegundos
        }

        // Inicializar el temporizador
        var redirectTimer = setTimeout(redirectLogin, 300000); // 30 segundos en milisegundos

        // Agregar eventos para detectar la actividad del usuario
        document.addEventListener("mousemove", resetTimer); // Interacción del mouse
        document.addEventListener("keypress", resetTimer); // Teclas presionadas
        document.addEventListener("click", resetTimer); // Clicks
