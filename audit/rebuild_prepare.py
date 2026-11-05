#!/usr/bin/env python3
"""Apply explicit device-safety/logging changes to the pinned 4.14.186 tree.
No version relabelling, forced module loads, root payloads or fake RT endpoint.
"""
from pathlib import Path
p=Path('drivers/dma/8250_mtk_dma.c')
s=p.read_text();start=s.index('static irqreturn_t mtk_dma_tx_interrupt(');end=s.index('\nstatic ',start+1);f=s[start:end]
old='struct mtk_dma_desc *d = c->desc;'
assert f.count(old)==1
f=f.replace(old,'struct mtk_dma_desc *d;',1)
old='\tspin_lock_irqsave(&c->vc.lock, flags);'
assert f.count(old)==1
f=f.replace(old,old+'''
	/* Historical dump shows a NULL TX descriptor in this interrupt path.
	 * Read descriptor under the channel lock and acknowledge stray IRQs.
	 * This is not evidence of fixing the current early-boot restart.
	 */
	d = c->desc;
	if (!d) {
		mtk_dma_chan_write(c, VFF_INT_FLAG, VFF_TX_INT_FLAG_CLR_B);
		spin_unlock_irqrestore(&c->vc.lock, flags);
		return IRQ_HANDLED;
	}
''',1)
s=s[:start]+f+s[end:];p.write_text(s)
p=Path('Makefile');s=p.read_text();old='--prefix=$(GCC_TOOLCHAIN_DIR)\n';assert old in s;s=s.replace(old,'--prefix=$(GCC_TOOLCHAIN_DIR)$(notdir $(CROSS_COMPILE))\n');p.write_text(s)
