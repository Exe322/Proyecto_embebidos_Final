#include <OneWire.h>
#include <DallasTemperature.h>


const int pinDatosDQ = 9; // Pin donde se conecta el bus 1-Wire
const int rele = 4; //salida del rele
float Sensibilidad=0.149; //sensibilidad en V/A para el sensor
float offset=0.1; // Equivale a la amplitud del ruido
float T_medida;
float I_peak;
String estado;

// Instancia a las clases OneWire y DallasTemperature
OneWire oneWireObjeto(pinDatosDQ);
DallasTemperature sensorDS18B20(&oneWireObjeto);


void setup() {
    //rele
    pinMode(rele,OUTPUT);
    digitalWrite(rele,HIGH);
    // Se inicia la comunicación serial
    Serial.begin(9600);
    // Se inicia el bus 1-Wire
    sensorDS18B20.begin(); 
    delay(500);
}

void loop() {
    // realizar una lectura de los datos recibidos por el puerto serial
    readSerialPort();
    // Se envían comandos para la toma de temperatura a los sensores
    sensorDS18B20.requestTemperatures();
    // Se leen y muestran los datos de los sensores DS18B20
    T_medida= sensorDS18B20.getTempCByIndex(0);
    //corriente peak 
    float I_peak = get_corriente();

    // filtro de corriente negativa
    if (I_peak<= 0.0){
      I_peak = 0.0; 
      Serial.print(T_medida);
      Serial.print(',');
      Serial.print(I_peak,3);
      Serial.print('\n');
      
    }
    else{
      Serial.print(T_medida);
      Serial.print(',');
      Serial.print(I_peak,3); //mostrar corriente con 3 decimales
      Serial.print('\n');
      
    }
    // condicional de la variable estado para encender relé
    if (estado=="ON"){
      digitalWrite(rele,LOW);
      
    }
    // condicional de la variable estado para apagar relé
    else if (estado=="OFF"){
      digitalWrite(rele,HIGH);
      
      }
    //tiempo de espera
    delay(1000); 
   
}
//función para realizar la medicion de corriente
float get_corriente()
{
  //variables
  float voltajeSensor;
  float corriente=0;
  long tiempo=millis();
  float Imax=0;
  float Imin=0;
  while(millis()-tiempo<500)//realizamos mediciones durante 0.5 segundos
  { 
    voltajeSensor = analogRead(A0) * (5.0 / 1023.0);//lectura del sensor
    corriente=0.9*corriente+0.1*((voltajeSensor-2.5)/Sensibilidad); //Ecuación  para obtener la corriente
    if(corriente>Imax)Imax=corriente;
    if(corriente<Imin)Imin=corriente;
  }
  //corriente promedio compensada por un offset
  return(((Imax-Imin)/2)-offset);
}

// funcion para recibir los bytes
void readSerialPort() {
  // definir la variable estado como vacía
  estado = "";
  //condicional de datos recibidos
  if (Serial.available()) {
    delay(10);
    // crear bucle para crear las palabas ON y OFF en la variable estado
    while (Serial.available() > 0) {
      estado += (char)Serial.read();
    }
    //borrar buffer de entrada
    Serial.flush();
  }
}
