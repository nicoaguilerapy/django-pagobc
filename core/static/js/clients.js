$("#select-identificador").hide();

$("#type_payment").on('change', function(){
    if($('#type_payment').val()=='2'){
        $("#select-identificador").show();
    }else{
        $("#select-identificador").hide();
        $('#type_payment').val('1')
    }
});

    $(document).keyup(function(event) {
    if (event.which === 13) {
        sendForm();
    }
    });

    function sendForm() {
        var send_obj = {
            client: $("#client_id").val(),
            type_document: $("#type_document").val(),
            document: $("#search_document").val(),
            concept: $("#concept").val(),
            mount: $("#mount").val(),
            status: $("#status").val(),
            type_payment: $("#type_payment").val(),
            identificador: $("#identificador").val(),
            datepicker: $("#datepicker").val()
            };

            console.log(send_obj)

        $.ajax({
            type: 'POST',
            url: '/payment/create/',
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            data: JSON.stringify(send_obj),
            headers: {'X-CSRFToken':getCookie('csrftoken')},
            success:function(data){
                if(data.cod == "000"){
                    console.log('agregado')
                    alertSucces('crear Pago', data.message);
                    window.location.href = "{% url 'payment_list' %}" ;
                }
                else{
                    console.log(data.message)
                    alertError('Crear Pago', JSON.parse(JSON.stringify(data.message)));
                }
            },
              error:function(){     
                alertError('error', 'Error Inesperado del Servidor');
              }
            });
        }

    function getClient(list) {
        var sw = -1;
        for (let i = 0; i < list.length; i++) {
            if($('#search_document').val() == list[i].document){
                sw = i
            }
        }

        if(sw != -1){
            $('#type_document').val(list[sw].type_document)
            $('#client_name').val(list[sw].name)
            $('#client_id').val(list[sw].id)
        }else{
            $('#type_document_aux').val("--")
            $('#client_name').val("Cliente no Encontrado")
            $('#client_id').val("-1")
        }
    }