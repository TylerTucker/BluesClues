/* Page scan state
 *
 * Copyright 2020 Etienne Helluy-Lafont, Univ. Lille, CNRS.
 *
 * This file is part of Project Ubertooth.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <ubtbr/cfg.h>
#include <ubtbr/btctl_intf.h>
#include <ubtbr/btphy.h>
#include <ubtbr/bb.h>
#include <ubtbr/tdma_sched.h>
#include <ubtbr/scan_task.h>
#include <ubtbr/rx_task.h>
#include <ubtbr/tx_task.h>
#include <ubtbr/slave_state.h>
#include <ubtbr/elapsed_time.h>

#define PAGE_SCAN_MAX_TICKS (CLKN_RATE*60)
#define TX_PREPARE_IDX	1  // We will transmit at clkn1_0 = 2

unsigned long long int arr [262] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0xF8E61A3EAD0C};
//0xE8A73077AD02};

struct {
	fhs_info_t fhs_info;
	uint32_t clkn_start;
} page_scan_state;

static void page_scan_schedule(unsigned delay);

static int page_scan_canceled(void)
{
	return btctl_get_state() != BTCTL_STATE_PAGE_SCAN;
}

static void page_scan_tx_cb(void *arg)
{
	cprintf("fhs: ba=%llx clk27_2=%x lta=%d\n",
		page_scan_state.fhs_info.bdaddr,
		page_scan_state.fhs_info.clk27_2,
		page_scan_state.fhs_info.lt_addr);

		elapsed_time_init();


	// Mitigation
	elapsed_time_start(0);
	// Check if address exists in array
	int arrLen = sizeof arr / sizeof arr[0];
  int isElementPresent = 0;
  for (int i = 0; i < arrLen; i++) {
      if (arr[i] == page_scan_state.fhs_info.bdaddr) {
          isElementPresent = 1;
          break;
      }
	}
	// if (page_scan_state.fhs_info.bdaddr == arr[0]) {
	if (isElementPresent) {
		elapsed_time_stop(0);
		cprintf("Elapsed Time=%x\n", elapsed_time_diff(0));
		// clock_gettime(CLOCK_REALTIME, &stop);
		// accum = (stop.tv_sec - start.tv_sec) + (stop.tv_nsec - start.tv_nsec) / BILLION;
		// cprintf("%lf\n", accum);
		// end = clock();
		// time(&end_t);
		// cpu_time_used = (end - start);

		// cprintf("time=%d\n", cpu_time_used);
		// cprintf("clock=%d\n", clock());
		// page_scan_state.fhs_info.clk27_2 = difftime(end_t, start_t);
		// cprintf("%f\n", stop - start);
		// cprintf("fhs: ba=%llx clk27_2=%d lta=%d\n",
		// 	page_scan_state.fhs_info.bdaddr,
		// 	page_scan_state.fhs_info.clk27_2,
		// 	page_scan_state.fhs_info.lt_addr);
		// sprintf(output,"%f", 10.0);
		// snprintf(output, 50, "%f", 10.0);
		slave_state_init(page_scan_state.fhs_info.bdaddr,
				page_scan_state.fhs_info.lt_addr);
	}
}

/* RX FHS cb */
static int page_scan_rx_fhs_cb(msg_t *msg, void *arg, int time_offset)
{
	btctl_hdr_t *h = (btctl_hdr_t*)msg->data;
	btctl_rx_pkt_t *pkt;

	if (page_scan_canceled())
	{
		cprintf("page scan canceled\n");
		goto end;
	}
	if (h->type != BTCTL_RX_PKT)
		DIE("paging : expect acl rx");
	pkt = (btctl_rx_pkt_t *)h->data;
	if (BBPKT_GOOD_CRC(pkt))
	{
		if (pkt->bb_hdr.type != BB_TYPE_FHS)
		{
			cprintf("(bad type %d)", pkt->bb_hdr.type);
			goto end;
		}
		// Parse fhs to get bdaddr/clkn/ltaddr
		bbpkt_decode_fhs(pkt->bt_data, &page_scan_state.fhs_info);


		// Set slave clkn
		btphy.slave_clkn = (page_scan_state.fhs_info.clk27_2<<2)
				 + (btphy.slave_clkn-pkt->clkn);

		/* Schedule TX ID(3)*/
		tx_task_schedule(3&(TX_PREPARE_IDX-CUR_SLAVE_SLOT_IDX()),
			page_scan_tx_cb, NULL,
			NULL, NULL); 	// no header / no payload

	}
	else{
		page_scan_schedule(0);
	}
end:
	msg_free(msg);
	return 0;
}

/* RX ID(1) cb */
static void page_scan_rx_id_cb(int sw_detected, void *arg)
{
	unsigned delay;
	if(page_scan_canceled())
	{
		cprintf("page scan canceled\n");
		return;
	}
	if (sw_detected)
	{
		/* we should be at slave_clk = 0, prepare in one slot*/
		cprintf("!");
		/* Schedule TX ID(2) */
		delay = 3&(TX_PREPARE_IDX-CUR_SLAVE_SLOT_IDX());
		tx_task_schedule(delay,
			NULL, NULL,	// no tx callback
			NULL, NULL); 	// no header / no payload

		/* Schedule rx FHS */
		rx_task_schedule(delay+2,
			page_scan_rx_fhs_cb, NULL,	// ID rx callback
			1			// FHS packet has payload
			);
	}
	else
	{
		page_scan_schedule(0);
	}
}

static void page_scan_schedule(unsigned delay)
{
	if (MASTER_CLKN >= page_scan_state.clkn_start + PAGE_SCAN_MAX_TICKS)
	{
		cprintf("page scan timeout\n");
		btctl_set_state(BTCTL_STATE_STANDBY, BTCTL_REASON_TIMEOUT);
		return;
	}
	scan_task_schedule(delay, page_scan_rx_id_cb, NULL);
}

/*
 * Page slave
 */
void page_scan_state_setup(void)
{
	btphy_set_mode(BT_MODE_PAGE_SCAN, btphy.my_lap, btphy.my_uap);
	btctl_set_state(BTCTL_STATE_PAGE_SCAN, BTCTL_REASON_SUCCESS);
	page_scan_state.clkn_start = MASTER_CLKN+1;
	page_scan_schedule(1);
}
