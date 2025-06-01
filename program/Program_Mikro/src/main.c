#include <avr/interrupt.h>
#include <avr/io.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <util/delay.h>

#define BAUD 115200
#define USE_DOUBLE_SPEED 1

#if USE_DOUBLE_SPEED
#define UBRR_VALUE ((F_CPU / (8UL * BAUD)) - 1)
#else
#define UBRR_VALUE ((F_CPU / (16UL * BAUD)) - 1)
#endif

volatile uint8_t adc_enabled = 0;
volatile uint8_t do_enabled = 0;
volatile uint8_t di_enabled = 0;
volatile uint8_t adc_looping = 0;
volatile uint8_t di_looping = 0;
volatile uint8_t adc_loop = 0;
volatile uint8_t di_loop = 0;

volatile uint16_t adc_values[5] = {0};
volatile uint8_t adc_channel = 0;

volatile uint8_t output_state[4] = {0};
volatile uint8_t digital_inputs[3] = {0};

char rx_buffer[32];
volatile uint8_t rx_index = 0;
uint8_t adc_request_channel = 0xFF;
uint8_t di_request_channel = 0xFF;
uint8_t do_request_channel = 0xFF;
uint8_t do_request_state = 0;

// USART Functions
void USART_Init(void) {
#if USE_DOUBLE_SPEED
  UCSR0A |= (1 << U2X0);
#else
  UCSR0A &= ~(1 << U2X0);
#endif
  UBRR0H = (unsigned char)(UBRR_VALUE >> 8);
  UBRR0L = (unsigned char)UBRR_VALUE;
  UCSR0B = (1 << RXEN0) | (1 << TXEN0) | (1 << RXCIE0);
  UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);
}

void USART_Transmit(unsigned char data) {
  while (!(UCSR0A & (1 << UDRE0)));
  UDR0 = data;
}

void USART_SendString(const char* str) {
  while (*str) {
    USART_Transmit(*str++);
  }
}

// ADC
void ADC_Init() {
  ADMUX = (1 << REFS0);
  ADCSRA = (1 << ADEN) | (1 << ADPS2);
}

uint16_t ADC_Read(uint8_t channel) {
  ADMUX = (1 << REFS0) | (channel & 0x07);
  ADCSRA |= (1 << ADSC);
  while (ADCSRA & (1 << ADSC));
  return ADC;
}

// Timer
void Timer1_Init_100ms() {
  TCCR1A = 0;
  TCCR1B = (1 << WGM12) | (1 << CS12);
  OCR1A = 6250 - 1;
  TIMSK1 = (1 << OCIE1A);
}

ISR(TIMER1_COMPA_vect) {
  if (adc_enabled && (adc_loop || adc_request_channel < 5)) {
    for (uint8_t ch = 0; ch < 5; ch++) {
      if (adc_loop || adc_request_channel == ch) {
        uint16_t val = ADC_Read(ch);
        char buf[32];
        snprintf(buf, sizeof(buf), "ADC%d=%u\r\n", ch, val);
        USART_SendString(buf);
      }
    }
    adc_request_channel = 0xFF;
  }

  if (di_enabled && (di_loop || di_request_channel < 3)) {
    digital_inputs[0] = (PINB >> 1) & 1;
    digital_inputs[1] = (PINB >> 2) & 1;
    digital_inputs[2] = (PINB >> 3) & 1;

    for (uint8_t i = 0; i < 3; i++) {
      if (di_loop || di_request_channel == i) {
        char buf[16];
        snprintf(buf, sizeof(buf), "IN%d=%d\r\n", i, digital_inputs[i]);
        USART_SendString(buf);
      }
    }
    di_request_channel = 0xFF;
  }

  if (do_enabled) {
    // Terapkan status output berdasarkan output_state[]
    if (output_state[0])
      PORTD |= (1 << PD5);
    else
      PORTD &= ~(1 << PD5);  // OUT1
    if (output_state[1])
      PORTD |= (1 << PD6);
    else
      PORTD &= ~(1 << PD6);  // OUT2
    if (output_state[2])
      PORTD |= (1 << PD7);
    else
      PORTD &= ~(1 << PD7);  // OUT3
    if (output_state[3])
      PORTB |= (1 << PB0);
    else
      PORTB &= ~(1 << PB0);  // OUT4
  }
}

ISR(USART_RX_vect) {
  char c = UDR0;
  if (c == '\n' || c == '\r') {
    rx_buffer[rx_index] = '\0';

    if (strcmp(rx_buffer, "ADC_Set") == 0)
      adc_enabled = 1;
    else if (strcmp(rx_buffer, "DI_Set") == 0)
      di_enabled = 1;
    else if (strcmp(rx_buffer, "DO_Set") == 0)
      do_enabled = 1;
    else if (strncmp(rx_buffer, "ADC", 3) == 0 && rx_buffer[4] == '\0')
      adc_request_channel = rx_buffer[3] - '0';
    else if (strncmp(rx_buffer, "IN", 2) == 0 && rx_buffer[3] == '\0')
      di_request_channel = rx_buffer[2] - '0';

    else if (strncmp(rx_buffer, "OUT", 3) == 0 && rx_buffer[5] == '\0') {
      uint8_t out_index = rx_buffer[3] - '1';  // OUT1 → index 0
      if (out_index < 4) {
        output_state[out_index] = rx_buffer[4] - '0';  // '1' = ON, '0' = OFF
      }
    }

    rx_index = 0;
  } else {
    if (rx_index < sizeof(rx_buffer) - 1) {
      rx_buffer[rx_index++] = c;
    }
  }
  if (strcmp(rx_buffer, "ADC_Loop") == 0) {
    adc_looping = 1;
    adc_enabled = 1;
  } else if (strcmp(rx_buffer, "DI_Loop") == 0) {
    di_looping = 1;
    di_enabled = 1;
  } else if (strcmp(rx_buffer, "ADC_Stop") == 0) {
    adc_looping = 0;
  } else if (strcmp(rx_buffer, "DI_Stop") == 0) {
    di_looping = 0;
  }
  if (strcmp(rx_buffer, "ADC_Loop") == 0)
    adc_loop = 1;
  else if (strcmp(rx_buffer, "ADC_Stop") == 0)
    adc_loop = 0;
  else if (strcmp(rx_buffer, "DI_Loop") == 0)
    di_loop = 1;
  else if (strcmp(rx_buffer, "DI_Stop") == 0)
    di_loop = 0;
}

int main(void) {
  USART_Init();
  ADC_Init();
  Timer1_Init_100ms();

  DDRC = 0x00;                                      // ADC input PC0-PC4
  DDRB |= (1 << PB0);                               // output PB0
  DDRB &= ~((1 << PB1) | (1 << PB2) | (1 << PB3));  // input PB1-3
  DDRD |= (1 << PD5) | (1 << PD6) | (1 << PD7);     // output PD5-7

  sei();

  while (1) {
  }
}
