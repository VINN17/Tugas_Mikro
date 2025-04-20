#include <avr/interrupt.h>
#include <avr/io.h>
#include <stdbool.h>
#include <util/delay.h>

#define F_CPU 16000000UL
#define BAUD 9600
#define MYUBRR ((F_CPU / 16 / BAUD) - 1)
bool pompa = false, kelembapan = false;
int flag_buzzer = 0;
uint8_t bar = 0;

#define LED1_on PORTB |= (1 << 7);    // PORTB &= ~(1 << 6);//led1
#define LED1_off PORTB &= ~(1 << 7);  // PORTB |= (1 << 6);//led1
#define LED2_on PORTB |= (1 << 6);    // led2
#define LED2_off PORTB &= ~(1 << 6);  // led2

int main() {
  init_GPIO();  // Inisialisasi pin
  init_UART(MYUBRR);
  LED2_on;

  const char *str;
  char buffer[10];
  int flag_bar_pb = 0;
  flag_buzzer = 0;
  while (1) {
    if ((PINB & (1 << 4))) {
      if (!(PINH & (1 << 6))) {   // sw3
        if ((PINH & (1 << 5))) {  // sw4
          pompa = true;
          kelembapan = false;
          LED1_on;
          LED2_off;
          uart_sendString("Kelembaban: Rendah, Pompa: ON \r\n");
          if (flag_bar_pb == 0) {
            flag_bar_pb = 1;
            if (flag_buzzer == 0) {
              flag_buzzer = 1;
              beep_buzzer();
            }
            for (uint8_t i = 0; i < 8; i++) {
              bar |= (1 << i);
              PORTA = (bar & 0xFF);
              for (uint8_t i = 0; i < 5; i++) {
                uart_sendString("Kelembaban: Rendah, Pompa: ON \r\n");
                _delay_ms(10);
              }
              _delay_ms(10);
            }
          } else {
            uart_sendString("Kelembaban: Rendah, Pompa: ON \r\n");
            _delay_ms(100);
          }
          _delay_ms(10);
        } else {  // sw4
          LED1_off;
          LED2_on;
          if (flag_bar_pb == 1) {
            flag_bar_pb = 2;
            if (flag_buzzer == 1) {
              flag_buzzer = 0;
              beep_buzzer();
            }
            PORTA = 0xFF;
            for (int i = 7; i >= 0; i--) {
              bar &= ~(1 << i);
              PORTA = bar;
              for (uint8_t i = 0; i < 1; i++) {
                uart_sendString("Kelembaban: Tinggi, Pompa: OFF \r\n");
                _delay_ms(50);
              }
              _delay_ms(10);
            }
            PORTA = 0x00;
          } else {
            pompa = false;
            kelembapan = true;
            flag_bar_pb = 0;
            uart_sendString("Kelembaban: Tinggi, Pompa: OFF \r\n");
            _delay_ms(10);
          }
          flag_bar_pb = 0;
        }  // sw4
      } else  // sw3
        LED1_off;
      if (!(PINH & (1 << 5))) {  // sw4
        LED1_off;
        LED2_on;
        if (flag_bar_pb == 1) {
          flag_bar_pb = 2;
          if (flag_buzzer == 1) {
            flag_buzzer = 0;
            beep_buzzer();
          }
          PORTA = 0xFF;
          for (int i = 7; i >= 0; i--) {
            bar &= ~(1 << i);
            PORTA = bar;
            for (uint8_t i = 0; i < 5; i++) {
              uart_sendString("Kelembaban: Tinggi, Pompa: OFF \r\n");
              _delay_ms(10);
            }
            _delay_ms(10);
          }
          PORTA = 0x00;
          flag_bar_pb = 0;
        } else {
          pompa = false;
          kelembapan = true;
          flag_bar_pb = 0;
          uart_sendString("Kelembaban: Tinggi, Pompa: OFF \r\n");
          _delay_ms(10);
        }
      }
    } else {
      if (pompa == false) {
        LED1_on;
        LED2_off;
        flag_buzzer = 1;
        if (flag_bar_pb == 0) {
          flag_bar_pb = 1;
          if (flag_buzzer != 0) {
            flag_buzzer = 1;
            beep_buzzer();
          }
          for (uint8_t i = 0; i < 8; i++) {
            bar |= (1 << i);
            PORTA = (bar & 0xFF);
            for (uint8_t i = 0; i < 5; i++) {
              // uart_sendString("Pompa: ON \r\n");
              uart_sendString("Kelembaban: Rendah, Pompa: ON \r\n");
              _delay_ms(10);
            }
            _delay_ms(10);
          }
        } else {
          // uart_sendString("Pompa: ON \r\n");
          uart_sendString("Kelembaban: Rendah, Pompa: ON \r\n");
          _delay_ms(50);
        }

        // beep_buzzer();
        // pompa = true;
      }

      if (pompa == true) {
        LED1_off;
        LED2_on;
        if (flag_bar_pb == 1) {
          flag_bar_pb = 2;
          if (flag_buzzer == 1) {
            flag_buzzer = 0;
            beep_buzzer();
          }
          PORTA = 0xFF;
          for (int i = 7; i >= 0; i--) {
            bar &= ~(1 << i);
            PORTA = bar;
            for (uint8_t i = 0; i < 1; i++) {
              // uart_sendString("Pompa: OFF \r\n");
              uart_sendString("Kelembaban: Tinggi, Pompa: Off \r\n");
              _delay_ms(50);
            }
            _delay_ms(10);
          }
          PORTA = 0x00;
        } else {
          // pompa = false;
          // kelembapan = true;
          // uart_sendString("Pompa: OFF \r\n");
          uart_sendString("Kelembaban: Tinggi, Pompa: Off \r\n");
          bar = 0;
          flag_bar_pb = 0;
          _delay_ms(10);
        }
      }
    }
  }
}

void init_GPIO() {
  DDRB |= (1 << 7) | (1 << 6) | (1 << 5);  // led
  // barled
  DDRA |= (1 << 7) | (1 << 6) | (1 << 5) | (1 << 4) | (1 << 3) | (1 << 2) |
          (1 << 1) | (1 << 0);
  DDRC |= (1 << 7) | (1 << 6);

  // pb
  DDRB &= ~(1 << 4);  // input
  PORTB |= (1 << 4);  // pillup

  DDRH &= ~((1 << 6) | (1 << 5));  // input
  PORTH |= (1 << 6) | (1 << 5);    // pullup
}

void init_UART(unsigned char ubrr) {
  // set baudrate
  UBRR0H = (unsigned char)(ubrr >> 8);
  UBRR0L = (unsigned char)(ubrr);

  // enable tx
  UCSR0B = 1 << TXEN0;

  // set format usartnya 8data bit, 1 bit stop
  UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);
}

void uart_send(unsigned char data) {
  while (!(UCSR0A & (1 << UDRE0)));
  UDR0 = data;
}

void uart_sendString(const char *str) {
  for (int i = 0; str[i] != '\0'; i++) {
    uart_send(str[i]);
  }
}

void itoa(uint8_t num, char *str) { sprintf(str, "%d", num); }

void beep_buzzer() {
  PORTB |= (1 << 5);  // Nyalakan buzzer
  _delay_ms(500);
  PORTB &= ~(1 << 5);  // Matikan buzzer
}

// void update_barLED(uint8_t level) {
//   PORTA = (level & 0xFF);
// }