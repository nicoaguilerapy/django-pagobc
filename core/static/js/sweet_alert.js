function alertError(type, message){
    html_error = ''
    for (let i = 0; i < message.length; i++) {
        console.log(message[i])
        html_error = html_error + '<p>'+message[i]+'</p>'
    }

    Swal.fire({
        icon: 'error',
        title: 'Error en '+type,
        html: html_error,
      })

}

function alertSucces(message){

    Swal.fire({
        icon: 'success',
        title: message,
        showConfirmButton: false,
        timer: 1500
      })

}
