const fetch = require('node-fetch');

async function testWebhook() {
    const webhookUrl = 'http://localhost:8000/webhook/stripe/';
    
    const eventData = {
        type: 'checkout.session.completed',
        data: {
            object: {
                id: 'cs_test_' + Math.floor(Math.random() * 1000000),
                customer: 'cus_test_' + Math.floor(Math.random() * 1000000),
                subscription: 'sub_test_' + Math.floor(Math.random() * 1000000),
                payment_intent: 'pi_test_' + Math.floor(Math.random() * 1000000),
                metadata: {
                    service_id: '1',
                    user_id: '1'
                }
            }
        }
    };

    console.log('Enviando solicitud al webhook...');
    console.log('URL:', webhookUrl);
    console.log('Datos:', JSON.stringify(eventData, null, 2));

    try {
        const response = await fetch(webhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(eventData)
        });

        const responseData = await response.json();
        console.log('Respuesta del servidor:');
        console.log('Status:', response.status);
        console.log('Datos:', responseData);
    } catch (error) {
        console.error('Error al realizar la solicitud:');
        console.error(error.message);
    }
}

testWebhook();