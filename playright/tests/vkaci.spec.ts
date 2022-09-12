import { test, expect, Page, Locator } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('http://localhost:8080/');
});

test('should have VK ACI in the title and can show the modals', async ({ page }) => {
  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/VK ACI/);

  const modals = [
    {
      tooltip: "Open VKACI information",
      id: "modal-default",
      title: "VKACI Information"
    },
    {
      tooltip: "Graph Legend",
      id: "modal-legend",
      title: "Graph Legend"
    },
    {
      tooltip: "Regenerate Topology",
      id: "modal-small",
      title: "Regenerate"
    },
  ]
  for (const m of modals) {
    const modal = await openModal(page, m.tooltip, m.id)
    await expect(modal).toContainText(m.title)
    await closeModal(modal)
    await expect(modal).toBeHidden()
  }
});

async function openModal(page: Page, tooltip: string, modalId: string) {
  // create a locator
  const infoModalBtn = page.locator(`[data-balloon="${tooltip}"]`);
  // Expect an attribute "to be strictly equal" to the value.
  await expect(infoModalBtn).toHaveAttribute('onclick', `openModal('${modalId}')`);
  // Click the get started link.
  await infoModalBtn.click();
  return page.locator(`#${modalId}`);
}

async function closeModal(modal: Locator) {
  const close = modal.locator(".modal__close");
  await close.click();
}

test('should have correct tabs', async ({ page }) => {
  const tabs = [
    {
      tab: "Cluster Topology",
      id: "ct_tab",
      text: ["Different Views","Namespaces"]
    },
    {
      tab: "Leaf Topology",
      id: "lt_tab",
      text: ["Type the leaf name"]
    },
    {
      tab: "Node Topology",
      id: "nt_tab",
      text: ["Type the node name"]
    },
    {
      tab: "Pod Topology",
      id: "pt_tab",
      text: ["Selected Namespace", "Type the pod name"]
    },
    {
      tab: "Topology Table",
      id: "tt_tab",
      text: ["Table Views", "Complete Topology"]
    },
  ]

  for (const t of tabs) {
    const infoTabTitle = page.locator(`id=${t.id}`);
    await infoTabTitle.click()
    await expect(infoTabTitle).toHaveText(t.tab);
    const  tabContent = page.locator("//div[@class='tab-pane active']")
    for (const text of t.text){
      await expect(tabContent).toContainText(text);
    }
  }
});

// test('should show the default graph topology', async ({ page }) => {
//   const viz = page.locator("id=viz")
//   await expect(viz).toHaveScreenshot('default.png')
// });

async function checkTab(page: Page, tabId: string, tab: string, object: string){
  await page.locator(`id=${tabId}`).click();
  await page.locator(`id=${tab}name`).fill(object);
  await page.locator(`id=${tab}Bttn`).click();
  const viz = page.locator(`id=viz_${tab}`);
  await page.waitForTimeout(2000)
  await expect(viz).toHaveScreenshot(`${tab}_topology.png`, { threshold: 0.3 })
}

test('should show the node topology graph', async ({ page }) => {
  await checkTab(page, "nt_tab", "node", "1234abc")
});

test('should show the leaf topology graph', async ({ page }) => {
  await checkTab(page, "lt_tab", "leaf", "leaf-204")
});

test('should show the pod topology graph', async ({ page }) => {
  await checkTab(page, "pt_tab", "pod", "dateformat")
});