//
//  STEditProfileViewController.m
//  Stamped
//
//  Created by Devin Doty on 6/8/12.
//
//

#import "STEditProfileViewController.h"
#import "EditProfileHeaderView.h"
#import "STTextFieldTableCell.h"
#import "EditProfileFooterView.h"
#import "StampCustomizeViewController.h"
#import "STS3Uploader.h"
#import "STLoadingCell.h"
#import "STAccountParameters.h"
#import "STAccount.h"
#import "STUserDetail.h"
#import "STStampedAPI.h"
#import "STNavigationItem.h"
#import "STBlockUIView.h"
#import "Util.h"
#import "STRootViewController.h"
#import "QuartzUtils.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"

#define kDeleteActionSheetTag 101
#define kCaptureActionSheetTag 201

@interface STEditProfileViewController () <UITextFieldDelegate>

@property (nonatomic, retain) STS3Uploader *avatarUploader;
@property (nonatomic, readwrite, retain) STAccountParameters* data;
@property (nonatomic, readonly, retain) NSArray* dataSource;
@property (nonatomic, readonly, retain) NSDictionary* namesForKeyPaths;
@property (nonatomic, readwrite, retain) id<STAccount> account;
@property (nonatomic, readwrite, retain) UIImage* image;
@property (nonatomic, readwrite, retain) UITextField* currentTextField;

- (NSString*)titleForKeyPath:(NSString*)keyPath;
- (NSInteger)totalIndexForKeyPath:(NSString*)keyPath;
- (NSString*)keyPathForTotalIndex:(NSInteger)index;

@end



@implementation STEditProfileViewController

@synthesize data = _data;
@synthesize account = _account;
@synthesize dataSource = _dataSource;
@synthesize avatarUploader = _avatarUploader;
@synthesize namesForKeyPaths = _namesForKeyPaths;
@synthesize image = _image;
@synthesize currentTextField = _currentTextField;

- (id)init {
    if (self = [super initWithStyle:UITableViewStyleGrouped]) {
        self.title = NSLocalizedString(@"Edit Profile", @"Edit Profile");
        _namesForKeyPaths = [[NSDictionary dictionaryWithObjectsAndKeys:
                              @"link", @"website",
                              @"phone number", @"phone",
                              @"username", @"screenName",
                              nil] retain];
        NSArray *secion1 = [NSArray arrayWithObjects:@"name", @"location", @"website", @"bio", nil];
        NSArray *secion2 = [NSArray arrayWithObjects:@"screenName", @"phone", nil];
        _dataSource = [[NSArray arrayWithObjects:secion1, secion2, nil] retain];
        _data = [[STAccountParameters alloc] init];
        id<STUserDetail> currentUser = [STStampedAPI sharedInstance].currentUser;
        NSArray* sharedKeys = [NSArray arrayWithObjects:@"name", @"location", @"website", @"bio", @"screenName", nil];
        for (NSString* sharedKey in sharedKeys) {
            [_data setValue:[(id)currentUser valueForKey:sharedKey] forKey:sharedKey];
        }
        _avatarUploader = [[STS3Uploader alloc] init];
    }
    return self;
}

- (void)dealloc
{
    [_data release];
    [_account release];
    [_dataSource release];
    [_avatarUploader release];
    [_image release];
    [_currentTextField release];
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
    self.tableView.allowsSelection = NO;
    
    STNavigationItem *cancelButton = [[[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Cancel", @"Cancel") style:UIBarButtonItemStyleDone target:self action:@selector(cancel:)] autorelease];
    self.navigationItem.leftBarButtonItem = cancelButton;
    
    [self.tableView reloadData];
    
    [[STStampedAPI sharedInstance] accountWithCallback:^(id<STAccount> account, NSError *error, STCancellation *cancellation) {
        self.account = account; 
        if (!account) {
            [Util warnWithMessage:@"There was a problem contacting the server." andBlock:^{
                UINavigationController* nav = [Util sharedNavigationController];
                if (nav.topViewController == self) {
                    [[Util sharedNavigationController] popViewControllerAnimated:YES];
                } 
            }];
        }
        else {
            self.data.phone = [account phone];
            if (!self.navigationItem.rightBarButtonItem) {
                STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Save", @"Save") style:UIBarButtonItemStyleDone target:self action:@selector(save:)];
                self.navigationItem.rightBarButtonItem = button;
                [button release];
            }
            [self.tableView reloadData];
        }
    }];
    
    STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.tableView.bounds];
    background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    [background setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
        drawGradient([UIColor colorWithRed:0.961f green:0.961f blue:0.957f alpha:1.0f].CGColor, [UIColor colorWithRed:0.898f green:0.898f blue:0.898f alpha:1.0f].CGColor, ctx);
    }];
    self.tableView.backgroundView = background;
    [background release];
    
    if (!self.tableView.tableFooterView) {
        
        EditProfileFooterView *view = [[EditProfileFooterView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 74.0f)];
        view.backgroundColor = [UIColor clearColor];
        view.delegate = (id<EditProfileFooterViewDelegate>)self;
        self.tableView.tableFooterView = view;
        [view release];
        
    }
    
    if (!self.tableView.tableHeaderView) {
        EditProfileHeaderView *view = [[EditProfileHeaderView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 145.0f)];
        self.tableView.tableHeaderView = view;
        view.delegate = (id<EditProfileHeaderViewDelegate>)self;
        [view release];
    }
    
}

#pragma mark - Actions

- (void)save:(id)sender {
    [self grabValueFromTextField:self.currentTextField];
    UIActivityIndicatorView* loadingView = [[[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleWhiteLarge] autorelease];
    loadingView.frame = CGRectMake(0, 0, self.view.frame.size.width, self.view.frame.size.height);
    [self.view addSubview:loadingView];
    [loadingView startAnimating];
    [[STStampedAPI sharedInstance] updateAccountWithAccountParameters:self.data andCallback:^(id<STUserDetail> user, NSError *error, STCancellation *cancellation) {
        if (user) {
            if (self.image) {
                [STStampedAPI sharedInstance].currentUserImage = self.image;
            }
            [Util compareAndPopController:self animated:YES];
        }
        else {
            [Util warnWithMessage:error.localizedDescription andBlock:^{
                [Util compareAndPopController:self animated:YES];
            }];
        }
    }];
}

- (void)cancel:(id)sender {
    [Util compareAndPopController:self animated:YES];
}


#pragma mark - EditProfileFooterViewDelegate

- (void)editProfileFooterViewDeleteAccount:(EditProfileFooterView*)view {
    
    UIActionSheet *actionSheet = [[UIActionSheet alloc] initWithTitle:@"Are you sure you want delete your account?" delegate:(id<UIActionSheetDelegate>)self cancelButtonTitle:@"Cancel" destructiveButtonTitle:@"Delete Account" otherButtonTitles:nil];
    actionSheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
    actionSheet.tag = kDeleteActionSheetTag;
    [actionSheet showInView:self.view];
    [actionSheet release];
    
}


#pragma mark - EditProfileHeaderViewDelegate

- (void)editProfileHeaderViewChangePicture:(EditProfileHeaderView*)view {
    
    UIActionSheet *actionSheet = [[UIActionSheet alloc] initWithTitle:nil delegate:(id<UIActionSheetDelegate>)self cancelButtonTitle:nil destructiveButtonTitle:nil otherButtonTitles:nil];
    
    if ([UIImagePickerController isSourceTypeAvailable:UIImagePickerControllerSourceTypePhotoLibrary]) {
        [actionSheet addButtonWithTitle:@"Choose a Photo"];
    }
    
    if ([UIImagePickerController isSourceTypeAvailable:UIImagePickerControllerSourceTypeCamera]) {
        [actionSheet addButtonWithTitle:@"Take a Photo"];
    }
    
    actionSheet.tag = kCaptureActionSheetTag;
    [actionSheet addButtonWithTitle:NSLocalizedString(@"Cancel", nil)];
    actionSheet.cancelButtonIndex = [actionSheet numberOfButtons]-1;
    actionSheet.actionSheetStyle = UIActionSheetStyleBlackTranslucent;
    [actionSheet showInView:self.view];
    [actionSheet release];
    
}

- (void)editProfileHeaderViewChangeColor:(EditProfileHeaderView*)view {
    
    StampCustomizeViewController *controller = [[StampCustomizeViewController alloc] initWithColors:[view colors]];
    controller.delegate = (id<StampCustomizeViewControllerDelegate>)self;
    STRootViewController *navController = [[STRootViewController alloc] initWithRootViewController:controller];
    [self presentModalViewController:navController animated:YES];
    [navController release];
    [controller release];
    
}


#pragma mark - StampCustomizeViewControllerDelegate

- (void)stampCustomizeViewControllerCancelled:(StampCustomizeViewController*)controller {
    [self dismissModalViewControllerAnimated:YES];
}

- (void)stampCustomizeViewController:(StampCustomizeViewController*)controller doneWithColors:(NSArray*)colors {
    
    if (!colors || [colors count] < 2) return; // invalid colors
    
    if ([self.tableView.tableHeaderView respondsToSelector:@selector(setStampColors:)]) {
        [(EditProfileHeaderView*)self.tableView.tableHeaderView setStampColors:colors];
    }
    
    UIColor* primaryColor = [colors objectAtIndex:0];
    UIColor* secondaryColor = [colors objectAtIndex:1];
    self.data.primaryColor = primaryColor.hexString;
    self.data.secondaryColor = secondaryColor.hexString;
    [self dismissModalViewControllerAnimated:YES];
    
}


#pragma mark - UIImagePickerControllerDelegate

- (void)imagePickerController:(UIImagePickerController *)picker didFinishPickingMediaWithInfo:(NSDictionary *)info {
    
    [picker dismissModalViewControllerAnimated:YES];    
    if ([info objectForKey:@"UIImagePickerControllerEditedImage"]) {
        UIImage *image = [info objectForKey:UIImagePickerControllerEditedImage];
        
        UIGraphicsBeginImageContext(CGSizeMake(500.0f, 500.0f));
        [image drawInRect:CGRectMake(0.0f, 0.0f, 500.0f, 500.0f)];
        image = UIGraphicsGetImageFromCurrentImageContext();
        UIGraphicsEndImageContext();
        
        if (self.tableView.tableHeaderView) {
            EditProfileHeaderView *header = (EditProfileHeaderView*)self.tableView.tableHeaderView;
            header.image = image;
        }
        self.image = nil;
        [self.avatarUploader cancel];
        NSString *path = [NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES) objectAtIndex:0];
		path = [[path stringByAppendingPathComponent:[[NSProcessInfo processInfo] processName]] stringByAppendingPathComponent:@"UploadTemp"];
        [[NSFileManager defaultManager] createDirectoryAtPath:path withIntermediateDirectories:YES attributes:nil error:nil];
        path = [path stringByAppendingPathComponent:@"temp.jpg"];
        [[NSFileManager defaultManager] removeItemAtPath:path error:nil];
        [UIImageJPEGRepresentation(image, 0.85) writeToFile:path atomically:NO];
        self.avatarUploader.filePath = path;
        [self.avatarUploader startWithProgress:^(float progress) {
            NSLog(@"%f", progress);
        } completion:^(NSString *path, BOOL finished) {
            self.data.tempImageURL = path;
            if (finished) {
                self.image = image;
            }
        }];
        
    }
    
}

- (void)imagePickerControllerDidCancel:(UIImagePickerController*)controller {
    [controller dismissModalViewControllerAnimated:YES];
}


#pragma mark - UITableViewDataSource

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    return 48.0f;
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    return 2;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    if (section == 1 && !self.account) return 1;
    return [(NSArray*)[_dataSource objectAtIndex:section] count];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if (!self.account && indexPath.section == 1) {
        return [[[STLoadingCell alloc] init] autorelease];
    }
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
    
    NSArray *array = [_dataSource objectAtIndex:indexPath.section];
    
    NSString* keyPath = [array objectAtIndex:indexPath.row];
    NSString* title = [self titleForKeyPath:keyPath];
    NSString* value = [self.data valueForKey:keyPath];
    cell.textField.returnKeyType = UIReturnKeyDone;
    cell.textField.enablesReturnKeyAutomatically = YES;
    cell.titleLabel.text = title;
    cell.textField.text = value ? value : @"";
    cell.textField.tag = [self totalIndexForKeyPath:keyPath];
    cell.textField.autocorrectionType = UITextAutocorrectionTypeNo;
    
    if ([keyPath isEqualToString:@"email"]) {
        cell.textField.keyboardType = UIKeyboardTypeEmailAddress;
    } else if ([keyPath isEqualToString:@"phone"]) {
        cell.textField.keyboardType = UIKeyboardTypeNumbersAndPunctuation;
    }
    
    return cell;
    
}

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
    if (section == 1) {
        return 30.0f;
    }
    return 0.0f;
}

- (CGFloat)tableView:(UITableView *)tableView heightForFooterInSection:(NSInteger)section {
    if (section == 1) {
        return 60.0f;
    }
    return 0.0f;
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
    
    if (section==1) {
        return [self labelWithTitle:@"Account"];
    }
    return nil;
    
}

- (UIView *)tableView:(UITableView *)tableView viewForFooterInSection:(NSInteger)section {
    if (section != 1) return nil;
    
    UIView *view = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 60.0f)];
    
    UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
    label.backgroundColor = [UIColor clearColor];
    label.textColor = [UIColor colorWithRed:0.600f green:0.600f blue:0.600f alpha:1.0f];
    label.shadowColor = [UIColor whiteColor];
    label.shadowOffset = CGSizeMake(0.0f, 1.0f);
    label.font = [UIFont systemFontOfSize:12];
    label.textAlignment = UITextAlignmentCenter;
    label.numberOfLines = 2;
    label.text = @"By adding your phone number,\nyour friends can find you more easily.";
    
    CGSize size = [label.text sizeWithFont:label.font constrainedToSize:CGSizeMake(view.bounds.size.width, CGFLOAT_MAX) lineBreakMode:UILineBreakModeWordWrap];
    CGRect frame = label.frame;
    frame.size = size;
    frame.origin.x = floorf((view.bounds.size.width-frame.size.width)/2);
    frame.origin.y = 10.0f;
    label.frame = frame;
    [view addSubview:label];
    [label release];
    
    return [view autorelease];
    
}


#pragma mark - UITextFieldDelegate

- (void)grabValueFromTextField:(UITextField*)textField {
    if (textField) {
        NSInteger index = textField.tag;
        NSString* keypath = [self keyPathForTotalIndex:index];
        [self.data setValue:textField.text forKey:keypath];
    }
}

- (void)textFieldDidBeginEditing:(UITextField *)textField {
    self.currentTextField = textField;
}

- (void)textFieldDidEndEditing:(UITextField *)textField {
    [self grabValueFromTextField:textField];
    self.currentTextField = nil;
}

- (BOOL)textFieldShouldReturn:(UITextField *)textField {
	[textField resignFirstResponder];
    return YES;
}

#pragma mark - UIActionSheetDelegate

- (void)actionSheet:(UIActionSheet *)actionSheet clickedButtonAtIndex:(NSInteger)buttonIndex {
    
    if (actionSheet.tag == kCaptureActionSheetTag) {
        
        if (buttonIndex == [actionSheet numberOfButtons]-1) return;
        
        UIImagePickerController *controller = [[UIImagePickerController alloc] init];
        controller.allowsEditing = YES;
        controller.delegate = (id<UIImagePickerControllerDelegate, UINavigationControllerDelegate>)self;
        
        if (buttonIndex == 0) {
            controller.sourceType = UIImagePickerControllerSourceTypePhotoLibrary;
        } else if (buttonIndex == 1) {
            controller.sourceType = UIImagePickerControllerSourceTypeCamera;
        }
        
        [self presentModalViewController:controller animated:YES];
        
    }
    
    else if (actionSheet.tag == kDeleteActionSheetTag) {
        if (actionSheet.cancelButtonIndex == buttonIndex) return;
        [[STStampedAPI sharedInstance] deleteAccountWithCallback:^(BOOL success, NSError *error, STCancellation *cancellation) {
            if (success) {
                [Util compareAndPopController:self animated:YES];
            }
            else {
                [Util warnWithAPIError:error andBlock:nil];
            }
        }];
    }
    
    
    
}

#pragma mark - Private

- (NSString *)titleForKeyPath:(NSString *)keyPath {
    NSString* alias = [self.namesForKeyPaths objectForKey:keyPath];
    if (alias) {
        return alias;
    }
    else {
        return keyPath;
    }
}

//TODO optimize
- (NSInteger)totalIndexForKeyPath:(NSString *)keyPath {
    NSInteger i = 0;
    for (NSInteger s = 0; s < self.dataSource.count; s++) {
        NSArray* array = [self.dataSource objectAtIndex:s];
        for (NSInteger r = 0; r < array.count; r++) {
            NSString* key = [array objectAtIndex:r];
            if ([key isEqualToString:keyPath]) {
                return i;
            }
            i++;
        }
    }
    return -1;
}

//OPTIMIZE
- (NSString *)keyPathForTotalIndex:(NSInteger)index {
    
    NSInteger i = 0;
    for (NSInteger s = 0; s < self.dataSource.count; s++) {
        NSArray* array = [self.dataSource objectAtIndex:s];
        for (NSInteger r = 0; r < array.count; r++) {
            if (i == index) {
                return [array objectAtIndex:r];
            }
            i++;
        }
    }
    return @"";
}

@end
