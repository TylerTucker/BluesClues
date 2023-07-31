/*
********************************************************************************
*                       MODULE TO MEASURE EXECUTION TIME
********************************************************************************
*/
#include <stdio.h>
#include <string.h>
#include <stdint.h>
/*
********************************************************************************
*                           CORTEX-M - DWT TIMER
********************************************************************************
*/

#define  ARM_CM_DEMCR      (*(uint32_t *)0xE000EDFC)
#define  ARM_CM_DWT_CTRL   (*(uint32_t *)0xE0001000)
#define  ARM_CM_DWT_CYCCNT (*(uint32_t *)0xE0001004)
#define ELAPSED_TIME_MAX_SECTIONS 1
/*
********************************************************************************
*                             Data Structure
********************************************************************************
*/

typedef  struct  elapsed_time {
    uint32_t  start;
    uint32_t  current;
    uint32_t  max;
    uint32_t  min;
} ELAPSED_TIME;

/*
********************************************************************************
*                      STORAGE FOR ELAPSED TIME MEASUREMENTS
********************************************************************************
*/

static  ELAPSED_TIME  elapsed_time_tbl[ELAPSED_TIME_MAX_SECTIONS];

/*
********************************************************************************
*                              MODULE INITIALIZATION
*
* Note(s): Must be called before any of the other functions in this module
********************************************************************************
*/

void  elapsed_time_init (void)
{
    uint32_t  i;


    if (ARM_CM_DWT_CTRL != 0) {                  // See if DWT is available
        ARM_CM_DEMCR      |= 1 << 24;            // Set bit 24
        ARM_CM_DWT_CYCCNT  = 0;
        ARM_CM_DWT_CTRL   |= 1 << 0;             // Set bit 0
    }
    for (i = 0; i < ELAPSED_TIME_MAX_SECTIONS; i++) {
        elapsed_time_clr(i);
    }
}

/*
********************************************************************************
*                  START THE MEASUREMENT OF A CODE SECTION
********************************************************************************
*/

void  elapsed_time_start (uint32_t  i)
{
    elapsed_time_tbl[i].start = ARM_CM_DWT_CYCCNT;
}

/*
********************************************************************************
*           STOP THE MEASUREMENT OF A CODE SECTION AND COMPUTE STATS
********************************************************************************
*/

void  elapsed_time_stop (uint32_t  i)
{
    uint32_t       stop;
    ELAPSED_TIME  *p_tbl;


    stop           = ARM_CM_DWT_CYCCNT;
    p_tbl          = &elapsed_time_tbl[i];
    p_tbl->current = stop - p_tbl->start;
    if (p_tbl->max < p_tbl->current) {
        p_tbl->max = p_tbl->current;
    }
    if (p_tbl->min > p_tbl->current) {
        p_tbl->min = p_tbl->current;
    }
}

/*
********************************************************************************
*                      CLEAR THE MEASUREMENTS STATS
********************************************************************************
*/

void  elapsed_time_clr (uint32_t  i)
{
    ELAPSED_TIME  *p_tbl;


    p_tbl          = &elapsed_time_tbl[i];
    p_tbl->start   = 0;
    p_tbl->current = 0;
    p_tbl->min     = 0xFFFFFFFF;
    p_tbl->max     = 0;
}

/*
********************************************************************************
*                      GET TIMING DIFFERENCE
********************************************************************************
*/

uint32_t elapsed_time_diff (uint32_t i)
{
  ELAPSED_TIME  *p_tbl;
  p_tbl = &elapsed_time_tbl[i];
  return p_tbl->current;
}
