//
//  SignupWelcomeViewController.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "SignupWelcomeViewController.h"
#import "StampColorPickerView.h"
#import "SocialSignupHeaderView.h"
#import "STTextFieldTableCell.h"
#import "StampCustomizeViewController.h"
#import "STTwitter.h"
#import "STAuth.h"
#import "STFacebook.h"
#import "STAvatarView.h"
#import "AccountManager.h"

@interface SignupWelcomeViewController ()

@end

@implementation SignupWelcomeViewController
@synthesize signupType=_signupType;

- (id)initWithType:(SignupWelcomeType)type {
    if ((self = [super initWithStyle:UITableViewStyleGrouped])) {
        _signupType = type;
        [STEvents addObserver:self selector:@selector(signupFinished:) event:EventTypeSignupFinished];
    }
    return self;
}

- (void)dealloc {
    [STEvents removeObserver:self];
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.navigationItem.leftBarButtonItem = nil;
    self.tableView.showsVerticalScrollIndicator = NO;
    self.tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
    self.tableView.allowsSelection = NO;
    
    if (!self.tableView.tableHeaderView) {
        
        SocialSignupHeaderView *header = [[SocialSignupHeaderView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 104.0f)];
        header.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        header.backgroundColor = [UIColor clearColor];
        self.tableView.tableHeaderView = header;
        
        if (_signupType == SignupWelcomeTypeTwitter) {
            
            NSDictionary *userDic = [[STTwitter sharedInstance] twitterUser];

            NSString *location = [userDic objectForKey:@"location"];
            if (location != nil && ![location isEqual:[NSNull null]]) {
                header.subTitleLabel.text = location;
            }
            NSString *description = [userDic objectForKey:@"description"];
            if (description != nil && ![location isEqual:[NSNull null]]) {
                header.detailLabel.text = description;
            }
            
            header.titleLabel.text = [userDic objectForKey:@"name"];
            [header.imageView setImageURL:[NSURL URLWithString:[userDic objectForKey:@"profile_image_url"]]];
            [header setNeedsLayout];

        } else if (_signupType == SignupWelcomeTypeFacebook) {
            
            NSDictionary *dictionary = [[STFacebook sharedInstance] userData];
            header.titleLabel.text = [dictionary objectForKey:@"name"];
            [header setNeedsLayout];

        }
        [header release];

    }
    
    if (!self.tableView.tableFooterView) {
        StampColorPickerView *view = [[StampColorPickerView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 220.0f)];
        view.backgroundColor = [UIColor clearColor];
        view.delegate = (id<StampColorPickerDelegate>)self;
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        self.tableView.tableFooterView = view;
        [view release];
    }
    
    if (!self.tableView.backgroundView) {
        STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.tableView.bounds];
        background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        [background setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
            drawGradient([UIColor colorWithRed:0.961f green:0.961f blue:0.957f alpha:1.0f].CGColor, [UIColor colorWithRed:0.898f green:0.898f blue:0.898f alpha:1.0f].CGColor, ctx);
        }];
        self.tableView.backgroundView = background;
        [background release];
    }
    
    if (!self.navigationItem.rightBarButtonItem) {
        STNavigationItem *item = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Next", @"Next") style:UIBarButtonItemStyleBordered target:self action:@selector(next:)];
        self.navigationItem.rightBarButtonItem = item;
        [item release];
    }
    
    if (!self.navigationItem.leftBarButtonItem) {
        STNavigationItem *item = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Cancel", @"Cancel") style:UIBarButtonItemStyleBordered target:self action:@selector(cancel:)];
        self.navigationItem.leftBarButtonItem = item;
        [item release];
    }
    
    
}

- (void)viewDidUnload {
    self.tableView.tableHeaderView=nil;
    self.tableView=nil;
    [super viewDidUnload];
}


#pragma mark - Notifications

- (void)signupFinished:(NSNotification*)notification {
    
    [self dismissModalViewControllerAnimated:YES];
    
}


#pragma mark - Actions

- (void)next:(id)sender {
    
    STTextFieldTableCell *cell = (STTextFieldTableCell*)[self.tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:0 inSection:0]];
    NSMutableDictionary *params = [[NSMutableDictionary alloc] init];

    if (_signupType == SignupWelcomeTypeTwitter) {
        
        NSDictionary *userDic = [[STTwitter sharedInstance] twitterUser];
        [params setObject:cell.textField.text forKey:@"username"];
        [params setObject:[[STTwitter sharedInstance] twitterToken] forKey:@"user_token"];
        [params setObject:[[STTwitter sharedInstance] twitterTokenSecret] forKey:@"user_secret"];

        NSString *name = [userDic objectForKey:@"name"];
        if (name != nil && ![name isEqual:[NSNull null]]) {
            [params setObject:name forKey:@"name"];
        } else {
            [params setObject:cell.textField.text forKey:@"name"];
        }
        
        [[STAuth sharedInstance] twitterSignupWithParams:params];
        NSLog(@"twitter signing up with params %@", params);
        
    } else if (_signupType == SignupWelcomeTypeFacebook) {
        
        NSDictionary *dictionary = [[STFacebook sharedInstance] userData];
        [params setObject:cell.textField.text forKey:@"username"];
        [params setObject:[[[STFacebook sharedInstance] facebook] accessToken] forKey:@"user_token"];
        
        NSString *name = [dictionary objectForKey:@"name"];
        if (name != nil && ![name isEqual:[NSNull null]]) {
            [params setObject:name forKey:@"name"];
        } else {
            [params setObject:cell.textField.text forKey:@"name"];
        }
        [[AccountManager sharedManager] createAccountWithFacebook:@"John Doe"
                                                       screenname:[params objectForKey:@"username"]
                                                        userToken:[params objectForKey:@"user_token"]
                                                            email:@"test3@stamped.com"];
        //[[STAuth sharedInstance] facebookSignupWithParams:params];
        NSLog(@"facebook signing up with params %@", params);

    } else if (_signupType == SignupWelcomeTypeEmail) {
        
     
        
    }
    
}

- (void)cancel:(id)sender {
    
    [self dismissModalViewControllerAnimated:YES];
    
}


#pragma mark - UITableViewDataSource

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    return 60.0f;
    
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    return 1;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    static NSString *CellIdentifier = @"CellIdentifier";
    
    STTextFieldTableCell *cell = (STTextFieldTableCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
       
        cell = [[[STTextFieldTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
        cell.textField.delegate = (id<UITextFieldDelegate>)self;
        cell.textField.returnKeyType = UIReturnKeyDone;
        cell.textField.autocapitalizationType = UITextAutocapitalizationTypeNone;
        cell.textField.autocorrectionType = UITextAutocorrectionTypeNo;
        
        if (_signupType == SignupWelcomeTypeTwitter) {
            
            cell.textField.text = [[STTwitter sharedInstance] twitterUsername];
            
        } else if (_signupType == SignupWelcomeTypeFacebook) {

            NSDictionary *dictionary = [[STFacebook sharedInstance] userData];
            if ([dictionary objectForKey:@"username"]) {
                cell.textField.text = [dictionary objectForKey:@"username"];
            }
            
        }
        
    }
    cell.titleLabel.text = @"username";
  
    
    return cell;
    
}

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
    
    return 30.0f;
    
}

- (CGFloat)tableView:(UITableView*)tableView heightForFooterInSection:(NSInteger)section {
    
    return 30.0f;
    
}

- (UIView*)labelWithTitle:(NSString*)title {
    
    UIView *view = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 30.0f)];
    
    UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
    label.backgroundColor = [UIColor clearColor];
    label.textColor = [UIColor colorWithRed:0.600f green:0.600f blue:0.600f alpha:1.0f];
    label.shadowColor = [UIColor whiteColor];
    label.shadowOffset = CGSizeMake(0.0f, 1.0f);
    label.font = [UIFont boldSystemFontOfSize:12];
    label.text = title;
    
    [label sizeToFit];
    CGRect frame = label.frame;
    frame.origin.x = 15.0f;
    frame.origin.y = floorf(((view.bounds.size.height-frame.size.height)/2) + 6.0f);
    label.frame = frame;
    [view addSubview:label];
    [label release];
    
    UIView *border = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, view.bounds.size.width, 1.0f)];
    border.autoresizingMask = UIViewAutoresizingFlexibleWidth;
    border.backgroundColor = [[UIColor blackColor] colorWithAlphaComponent:0.05f];
    [view addSubview:border];
    [border release];
    
    border = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 1.0f, view.bounds.size.width, 1.0f)];
    border.autoresizingMask = UIViewAutoresizingFlexibleWidth;
    border.backgroundColor = [[UIColor whiteColor] colorWithAlphaComponent:0.6f];
    [view addSubview:border];
    [border release];
    
    return [view autorelease];
    
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
    
    return [self labelWithTitle:@"Create your username"];
    
}

- (UIView*)tableView:(UITableView*)tableView viewForFooterInSection:(NSInteger)section {
    
    return [self labelWithTitle:@"Choose your stamp color"];
    
}


#pragma mark - StampCustomizeViewControllerDelegate

- (void)stampCustomizeViewControllerCancelled:(StampCustomizeViewController*)controller {
    [self dismissModalViewControllerAnimated:YES];
}

- (void)stampCustomizeViewController:(StampCustomizeViewController*)controller doneWithColors:(NSArray*)colors {
    [self dismissModalViewControllerAnimated:YES];
    
    if ([self.tableView.tableHeaderView respondsToSelector:@selector(setStampColors:)]) {
        [(SocialSignupHeaderView*)self.tableView.tableHeaderView setStampColors:colors];
    }
    
}


#pragma mark - StampColorPickerDelegate

- (void)stampColorPickerViewSelectedCustomize:(StampColorPickerView*)view {
    
    StampCustomizeViewController *controller = [[StampCustomizeViewController alloc] initWithColors:[view colors]];
    controller.delegate = (id<StampCustomizeViewControllerDelegate>)self;
    STRootViewController *navController = [[STRootViewController alloc] initWithRootViewController:controller];
    [self presentModalViewController:navController animated:YES];
    [navController release];
    [controller release];
    
}

- (void)stampColorPickerView:(StampColorPickerView*)view selectedColors:(NSArray*)colors {
    
    if ([self.tableView.tableHeaderView respondsToSelector:@selector(setStampColors:)]) {
        [(SocialSignupHeaderView*)self.tableView.tableHeaderView setStampColors:colors];
    }
    
}


#pragma mark - UITextFieldDelegate

- (BOOL)textFieldShouldReturn:(UITextField *)textField {
    [textField resignFirstResponder];
    return YES;
}


@end
