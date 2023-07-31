/*
********************************************************************************
*                       MODULE TO MEASURE EXECUTION TIME
********************************************************************************
*/

/*
********************************************************************************
*                MAXIMUM NUMBER OF ELAPSED TIME MEASUREMENT SECTIONS
********************************************************************************
*/

#define  ELAPSED_TIME_MAX_SECTIONS  10

/*
********************************************************************************
*                             FUNCTION PROTOTYPES
********************************************************************************
*/

void  elapsed_time_clr   (uint32_t  i);      // Clear measured values
void  elapsed_time_init  (void);             // Module initialization
void  elapsed_time_start (uint32_t  i);      // Start measurement
void  elapsed_time_stop  (uint32_t  i);      // Stop  measurement
uint32_t elapsed_time_diff  (uint32_t i);    // Get time difference
