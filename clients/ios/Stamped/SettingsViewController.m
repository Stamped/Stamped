//
//  SettingsViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/1/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "SettingsViewController.h"

#import "AccountManager.h"
#import "EditProfileViewController.h"
#import "SharingSettingsViewController.h"
#import "AboutUsViewController.h"
#import "WebViewController.h"
#import "TOSViewController.h"
#import "ECSlidingViewController.h"
#import "Util.h"

@implementation SettingsViewController

@synthesize tableView = _tableView;
@synthesize sharingView = sharingView_;


- (id)init {
    if (self = [super init]) {
    }
    return self;
}

- (void)didReceiveMemoryWarning {
  [super didReceiveMemoryWarning];
}

- (void)dealloc {
  self.tableView = nil;
  self.sharingView = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)backButtonClicked:(id)button {
  [self.slidingViewController anchorTopViewTo:ECRight];
}

- (void)viewDidLoad {
  [super viewDidLoad];

    if (!_tableView) {
        UITableView *tableView = [[UITableView alloc] initWithFrame:self.view.bounds style:UITableViewStylePlain];
        tableView.delegate = (id<UITableViewDelegate>)self;
        tableView.dataSource = (id<UITableViewDataSource>)self;
        [self.view addSubview:tableView];
        self.tableView = tableView;
        [tableView release];
    }
    
    UIBarButtonItem *backButton = [[UIBarButtonItem alloc] initWithTitle:@"Settings" style:UIBarButtonItemStyleBordered target:nil action:nil];
    self.navigationItem.backBarButtonItem = backButton;
    [backButton release];

}

- (void)viewDidUnload {
  self.tableView = nil;
  self.sharingView = nil;
  [super viewDidUnload];
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    [self.tableView deselectRowAtIndexPath:self.tableView.indexPathForSelectedRow animated:YES];
}


#pragma mark - Custom methods.

- (IBAction)doneButtonPressed:(id)sender {
  //[[STRootMenuView sharedInstance] toggle];
  //[self.presentingViewController dismissModalViewControllerAnimated:YES];
}


- (IBAction)editProfileButtonPressed:(id)sender {
  EditProfileViewController* vc = [[EditProfileViewController alloc] init];
  vc.user = [AccountManager sharedManager].currentUser;
  [self.navigationController pushViewController:vc animated:YES];
  [vc release];
}


- (IBAction)notificationsButtonPressed:(id)sender {
//  NotificationSettingsViewController* vc = [[NotificationSettingsViewController alloc] init];
//  [self.navigationController pushViewController:vc animated:YES];
//  [vc release];
}

- (IBAction)sharingButtonPressed:(id)sender {
  if (!sharingView_) {
    SharingSettingsViewController* vc = [[SharingSettingsViewController alloc] init];
    self.sharingView = vc;
    [vc release];
  }
  [self.navigationController pushViewController:self.sharingView animated:YES];
}

- (IBAction)aboutUsButtonPressed:(id)sender {
  AboutUsViewController* vc = [[AboutUsViewController alloc] init];
  [self.navigationController pushViewController:vc animated:YES];
  [vc release];
}

- (IBAction)FAQButtonPressed:(id)sender {
  WebViewController* vc = [[WebViewController alloc] initWithURL:[NSURL URLWithString:@"http://www.stamped.com/faq-mobile.html/"]];
  [self.navigationController pushViewController:vc animated:YES];
  [vc hideToolbar:YES];
  [vc release];
}

- (IBAction)logoutButtonPressed:(id)sender {
  NSLog(@"asdklfjafdjkl");
  UIActionSheet* sheet = [[[UIActionSheet alloc] initWithTitle:@"Are you sure?"
                                                      delegate:self
                                             cancelButtonTitle:@"Cancel"
                                        destructiveButtonTitle:@"Logout"
                                             otherButtonTitles:nil] autorelease];
  sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
  [sheet showInView:self.view];
}

- (IBAction)legalButtonPressed:(id)sender {
  TOSViewController* vc = [[TOSViewController alloc] init];
  [self.navigationController pushViewController:vc animated:YES];
  vc.doneButton.hidden = YES;
  [vc release];
}

- (IBAction)feedbackButtonPressed:(id)sender {
  WebViewController* vc = [[WebViewController alloc] initWithURL:[NSURL URLWithString:@"http://www.stamped.com/feedback-mobile.html/"]];
  [self.navigationController pushViewController:vc animated:YES];
  vc.webView.scalesPageToFit = YES;
  vc.shareButton.hidden = YES;
  [vc release];
}


#pragma mark - UIActionSheetDelegate methods.

- (void)actionSheet:(UIActionSheet*)actionSheet didDismissWithButtonIndex:(NSInteger)buttonIndex {
  if (buttonIndex == 0) {  // Logout.
    [self.parentViewController dismissModalViewControllerAnimated:NO];
    [[AccountManager sharedManager] logout];
  }
}

@end
