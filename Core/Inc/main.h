/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2021 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32g4xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

void HAL_TIM_MspPostInit(TIM_HandleTypeDef *htim);

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define Led_Pin GPIO_PIN_0
#define Led_GPIO_Port GPIOF
#define M2_Direction_Pin GPIO_PIN_0
#define M2_Direction_GPIO_Port GPIOA
#define M2_PWM_Pin GPIO_PIN_1
#define M2_PWM_GPIO_Port GPIOA
#define M1_Direction_Pin GPIO_PIN_2
#define M1_Direction_GPIO_Port GPIOA
#define M1_PWM_Pin GPIO_PIN_3
#define M1_PWM_GPIO_Port GPIOA
#define M3_Direction_Pin GPIO_PIN_4
#define M3_Direction_GPIO_Port GPIOA
#define M3_PWM_Pin GPIO_PIN_5
#define M3_PWM_GPIO_Port GPIOA
#define n_Sleep_Pin GPIO_PIN_6
#define n_Sleep_GPIO_Port GPIOA
#define Thrower_PWM_Pin GPIO_PIN_7
#define Thrower_PWM_GPIO_Port GPIOA
/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
