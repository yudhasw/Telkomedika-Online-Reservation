document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.flash-message');
    
    if (messages.length > 0) {
        messages.forEach(msg => {
            setTimeout(() => {
                msg.classList.remove('opacity-100');
                msg.classList.add('opacity-0');
                msg.classList.add('-translate-y-2'); 

                setTimeout(() => {
                    msg.remove();
                }, 500);
            }, 3000); 
        });
    }
});
