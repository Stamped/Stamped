//
//  SignupViewController.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "SignupViewController.h"
#import "SignupWelcomeViewController.h"
#import "STTextFieldTableCell.h"
#import "SignupFooterView.h"
#import <AddressBookUI/AddressBookUI.h>
#import "STAuth.h"
#import "LoginLoadingView.h"
#import "STEvents.h"
#import "STNavigationItem.h"
#import "STBlockUIView.h"
#import "Util.h"
#import "QuartzUtils.h"

@interface SignupViewController ()

@end

@implementation SignupViewController
@synthesize delegate;

- (id)init {
    if (self = [super initWithStyle:UITableViewStyleGrouped]) {
        self.title = NSLocalizedString(@"Sign up", @"Sign up");
        _dataSource = [[NSArray arrayWithObjects:@"full name", @"email", @"username", @"password", @"phone number", nil] retain];
        self.navigationItem.hidesBackButton = YES;
       
        [STEvents addObserver:self selector:@selector(signupFinished:) event:EventTypeSignupFinished];
        [STEvents addObserver:self selector:@selector(signupFailed:) event:EventTypeSignupFailed];

    }
    return self;
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    if (!self.navigationItem.leftBarButtonItem) {
        STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Cancel", @"Cancel") style:UIBarButtonItemStyleBordered target:self action:@selector(cancel:)];
        self.navigationItem.leftBarButtonItem = button;
        [button release];
    }
    
    if (!self.navigationItem.rightBarButtonItem) {
        STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"AutoFill", @"AutoFill") style:UIBarButtonItemStyleBordered target:self action:@selector(autoFill:)];
        self.navigationItem.rightBarButtonItem = button;
        [button release];
    }
    
    
    if (!self.tableView.backgroundView) {
        STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.tableView.bounds];
        background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        [background setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
            drawGradient([UIColor colorWithRed:0.961f green:0.961f blue:0.957f alpha:1.0f].CGColor, [UIColor colorWithRed:0.898f green:0.898f blue:0.898f alpha:1.0f].CGColor, ctx);
        }];
        self.tableView.backgroundView = background;
        [background release];
    }
    
    if (!self.tableView.tableFooterView) {
        
        SignupFooterView *view = [[SignupFooterView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 140.0f)];
        view.delegate = (id<SignupFooterViewDelegate>)self;
        view.backgroundColor = [UIColor clearColor];
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        self.tableView.tableFooterView = view;
        [view release];
        
    }
    
    self.tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
    
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
}

- (void)dealloc {
    [_dataSource release];
    [STEvents removeObserver:self];
    [super dealloc];
}


#pragma mark - Sign up

- (STAccountParameters*)accountParams {
    
    STAccountParameters *parameters = [[STAccountParameters alloc] init];
    
    NSInteger index = 0;
    for (NSString *key in _dataSource) {
        STTextFieldTableCell *cell = (STTextFieldTableCell*)[self.tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:index inSection:0]];
        switch (index) {
            case 0:
                parameters.name = cell.textField.text;
                break;
            case 1:
                parameters.email = cell.textField.text;
                break;
            case 2:
                parameters.screenName = cell.textField.text;
                break;
            case 3:
                break;
            case 4:
                parameters.phone = cell.textField.text;
                break;
            default:
                break;
        }
        index++;
    }
    
    return [parameters autorelease];
    
}

- (void)signup {
    
    STAccountParameters *parameters = [self accountParams];
    STTextFieldTableCell *cell = (STTextFieldTableCell*)[self.tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:3 inSection:0]];
    NSString *password = cell.textField.text;
    [self setLoading:YES];
    
    if (!password) {
        password = @"";
    }
    
    [[STAuth sharedInstance] signupWithPassword:password parameters:parameters];
    
}


#pragma mark - Notifications 

- (void)signupFinished:(NSNotification*)notification {
    
    SignupWelcomeViewController *controller = [[SignupWelcomeViewController alloc] initWithType:SignupWelcomeTypeEmail];
    controller.userInfo = [self accountParams];
    [self.navigationController pushViewController:controller animated:YES];
    [controller release];

}

- (void)signupFailed:(NSNotification*)notification {
    [Util warnWithAPIError:notification.object andBlock:nil];
    [self setLoading:NO];
    
}


#pragma mark - Getters

- (NSString*)username {
    
    STTextFieldTableCell *cell = (STTextFieldTableCell*)[self.tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:2 inSection:0]];
    return cell.textField.text;
    
}


#pragma mark - Setters

- (void)setLoading:(BOOL)loading {
    
    if (self.tableView.tableFooterView) {
        [(SignupFooterView*)self.tableView.tableFooterView setLoading:loading];
    }
    
    [UIView beginAnimations:nil context:NULL];
    [UIView setAnimationDuration:0.1f];
    for (NSInteger i = 0; i < [_dataSource count]; i++) {
        
        STTextFieldTableCell *cell = (STTextFieldTableCell*)[self.tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:i inSection:0]];
        if (cell) {
            if (loading) {
                [cell disable];
            } else {
                [cell enable];
            }
        }
        
    }
    [UIView commitAnimations];
    
}


#pragma mark - Actions

- (void)cancel:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(signupViewControllerCancelled:)]) {
        [self.delegate signupViewControllerCancelled:self];
    }
    
}

- (void)autoFill:(id)sender {
    
    ABPeoplePickerNavigationController *controller = [[ABPeoplePickerNavigationController alloc] init];
    controller.peoplePickerDelegate = (id<ABPeoplePickerNavigationControllerDelegate>)self;
    [self presentModalViewController:controller animated:YES];
    [controller release];
    
}


#pragma mark - ABPeoplePickerNavigationControllerDelegate

- (void)peoplePickerNavigationControllerDidCancel:(ABPeoplePickerNavigationController *)peoplePicker {
    [self dismissModalViewControllerAnimated:YES];
}

- (BOOL)peoplePickerNavigationController:(ABPeoplePickerNavigationController *)peoplePicker shouldContinueAfterSelectingPerson:(ABRecordRef)person {
    
    [self dismissModalViewControllerAnimated:YES];
    
    CFStringRef cfFirstName = ABRecordCopyValue(person, kABPersonFirstNameProperty);
    CFStringRef cfLastName = ABRecordCopyValue(person, kABPersonLastNameProperty);
    
    NSString *firstName = (NSString*)cfFirstName;
    NSString *lastName = (NSString*)cfLastName;
    
    if (firstName) {
        
        STTextFieldTableCell *cell = (STTextFieldTableCell*)[self.tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:0 inSection:0]];
        cell.textField.text = (lastName==nil) ? firstName : [NSString stringWithFormat:@"%@ %@", firstName, lastName];
    
        NSString *username = [NSString stringWithFormat:@"%@%@", firstName.lowercaseString, (lastName!=nil) ? lastName.lowercaseString : @""];
        if (username) {
            STTextFieldTableCell *cell = (STTextFieldTableCell*)[self.tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:2 inSection:0]];
            cell.textField.text = username;
        }
        
    }
    if (cfFirstName != NULL) {
        CFRelease(cfFirstName);
    }
    if (cfLastName != NULL) {
        CFRelease(cfLastName);
    }
    
    CFStringRef cfPhone = NULL;
    NSString *phone = nil;
    ABMultiValueRef phoneNumbers = ABRecordCopyValue(person, kABPersonPhoneProperty);
    if (ABMultiValueGetCount(phoneNumbers) > 0) {
        cfPhone = ABMultiValueCopyValueAtIndex(phoneNumbers, 0);;
        phone = (NSString*)cfPhone;
    }
    if (phone) {
        STTextFieldTableCell *cell = (STTextFieldTableCell*)[self.tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:4 inSection:0]];
        cell.textField.text = phone;
    }
    if (cfPhone!=NULL) {
        CFRelease(cfPhone);
    }
    if (phoneNumbers!=NULL) {
        CFRelease(phoneNumbers);
    }
    
    NSString *email = nil;
    ABMultiValueRef emails = ABRecordCopyValue(person, kABPersonEmailProperty);
    if (ABMultiValueGetCount(emails) > 0) {
        email = (NSString*)ABMultiValueCopyValueAtIndex(emails, 0);
    }
    if (emails!=NULL) {
        CFRelease(emails);
    }
    
    if (email) {
        STTextFieldTableCell *cell = (STTextFieldTableCell*)[self.tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:1 inSection:0]];
        cell.textField.text = email;
    }
    [email release];
    
    return NO;
}


#pragma mark - UITableViewDataSource

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    return 48.0f;
    
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    return [_dataSource count];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    static NSString *CellIdentifier = @"CellIdentifier";
    
    STTextFieldTableCell *cell = (STTextFieldTableCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[[STTextFieldTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
        cell.textField.delegate = (id<UITextFieldDelegate>)self;
        cell.textField.autocapitalizationType = UITextAutocapitalizationTypeNone;
        cell.textField.autocorrectionType = UITextAutocorrectionTypeNo;
        cell.titleLabel.textColor = [UIColor colorWithWhite:0.6f alpha:1.0f];
        cell.titleLabel.textAlignment = UITextAlignmentRight;
    }
    
    cell.textField.returnKeyType = (indexPath.row == [_dataSource count]-1) ? UIReturnKeyDone : UIReturnKeyNext;
    cell.titleLabel.text = [_dataSource objectAtIndex:indexPath.row];
    
    if ((indexPath.row == [_dataSource count]-1)) {
        cell.textField.placeholder = @"optional";
    }
    cell.textField.secureTextEntry = (indexPath.row==3);
    cell.textField.autocorrectionType = UITextAutocorrectionTypeNo;
    cell.textField.autocapitalizationType = (indexPath.row==0) ? UITextAutocapitalizationTypeWords : UITextAutocapitalizationTypeNone;
    
    if (indexPath.row == 1) {
        cell.textField.keyboardType = UIKeyboardTypeEmailAddress;
    } else if (indexPath.row == 4) {
        cell.textField.keyboardType = UIKeyboardTypeNumbersAndPunctuation;
    }
    
    return cell;
    
}


#pragma mark - UITextFieldDelegate

- (BOOL)textFieldShouldReturn:(UITextField *)textField {
    
    if (textField.returnKeyType == UIReturnKeyDone) {
        [textField resignFirstResponder];
        return YES;
    }
    
    NSIndexPath *indexPath = [self.tableView indexPathForCell:(UITableViewCell*)textField.superview];
    if (indexPath && indexPath.row < [_dataSource count]) {
        STTextFieldTableCell *cell = (STTextFieldTableCell*)[self.tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:indexPath.row+1 inSection:0]];
        if (cell) {
            [cell.textField becomeFirstResponder];
            [self.tableView scrollToRowAtIndexPath:[NSIndexPath indexPathForRow:indexPath.row+1 inSection:0] atScrollPosition:UITableViewScrollPositionMiddle animated:YES];
        }
    }
    
    return YES;

}


#pragma mark - SignupFooterViewDelegate


- (void)signupFooterViewCreate:(SignupFooterView*)view {
    
    [self setLoading:YES];
    [self.tableView endEditing:YES];

    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, 0.3f * NSEC_PER_SEC), dispatch_get_main_queue(), ^(void){
        [self signup];
    });
    

}

- (void)signupFooterViewTermsOfUse:(SignupFooterView *)view {
    
}

- (void)signupFooterViewPrivacy:(SignupFooterView *)view {
    
}

@end
