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

#define kDeleteActionSheetTag 101
#define kCaptureActionSheetTag 201

@interface STEditProfileViewController ()
@property(nonatomic,retain) STS3Uploader *avatarUploader;
@end

@implementation STEditProfileViewController
@synthesize avatarUploader;

- (id)init {
    if (self = [super initWithStyle:UITableViewStyleGrouped]) {
        
        self.title = NSLocalizedString(@"Edit Profile", @"Edit Profile");
        NSArray *secion1 = [NSArray arrayWithObjects:@"full name", @"location", @"link", @"bio", nil];
        NSArray *secion2 = [NSArray arrayWithObjects:@"username", @"email", @"password", @"phone number", nil];
        _dataSource = [[NSArray arrayWithObjects:secion1, secion2, nil] retain];
        
    }
    return self;
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
    self.tableView.allowsSelection = NO;
    
    /*
     if (!self.navigationItem.leftBarButtonItem) {
     
     STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Cancel", @"Cancel") style:UIBarButtonItemStyleBordered target:self action:@selector(cancel:)];
     self.navigationItem.leftBarButtonItem = button;
     [button release];
     
     }
     */
    
    
    if (!self.navigationItem.rightBarButtonItem) {
        
        STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Save", @"Save") style:UIBarButtonItemStyleDone target:self action:@selector(save:)];
        self.navigationItem.rightBarButtonItem = button;
        [button release];
        
    }
    
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

- (void)viewDidUnload {
    [super viewDidUnload];
}


#pragma mark - Actions

- (void)save:(id)sender {
}

- (void)cancel:(id)sender {
    [[Util sharedNavigationController] popViewControllerAnimated:YES];
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
    
    if ([self.tableView.tableHeaderView respondsToSelector:@selector(setStampColors:)]) {
        [(EditProfileHeaderView*)self.tableView.tableHeaderView setStampColors:colors];
    }
    
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
            header.imageView.imageView.image = image;
        }
        
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
    return [_dataSource count];
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    return [(NSArray*)[_dataSource objectAtIndex:section] count];
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
    
    NSArray *array = [_dataSource objectAtIndex:indexPath.section];
    
    cell.textField.returnKeyType = UIReturnKeyDone;
    cell.titleLabel.text = [array objectAtIndex:indexPath.row];
    cell.textField.secureTextEntry = [cell.titleLabel.text isEqualToString:@"password"];
    cell.textField.autocorrectionType = UITextAutocorrectionTypeNo;
    
    if (indexPath.section == 1 && indexPath.row == 1) {
        cell.textField.keyboardType = UIKeyboardTypeEmailAddress;
    } else if (indexPath.section == 1 && indexPath.row == 3) {
        cell.textField.keyboardType = UIKeyboardTypeNumbersAndPunctuation;
    }
    
#warning tempoary code to fill fields
    
    id<STUserDetail> user = [[STStampedAPI sharedInstance] currentUser];
    if (indexPath.section == 0) {
        
        switch (indexPath.row) {
            case 0:
                cell.textField.text = user.name;
                break;
            case 1:
                cell.textField.text = user.location;
                break;
            case 2:
                cell.textField.text = user.website;
                break;
            case 3:
                cell.textField.text = user.bio;
                break;
            default:
                break;
        }
        
    } else if (indexPath.section == 1) {
        
        switch (indexPath.row) {
            case 0:
                cell.textField.text = user.screenName;
                break;
            case 1:
                if ([user respondsToSelector:@selector(email)]) {
                    cell.textField.text = [(id)user email];
                }
                break;
            case 2:
            case 3:
                break;
            default:
                break;
        }
        
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

- (BOOL)textFieldShouldReturn:(UITextField *)textField {
    
    if (textField.returnKeyType == UIReturnKeyDone) {
        [textField resignFirstResponder];
        return YES;;
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
        
        
    }
    
    
    
}



@end
