function showAlert(type){

    if(type == 'user-error'){
        Swal.fire({
            icon: 'info',
            title: 'Las contraseñas deben ser iguales',
            showConfirmButton: false,
            timer: 1500
          })
    }
    
}
