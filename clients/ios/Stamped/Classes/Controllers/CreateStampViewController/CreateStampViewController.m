//
//  CreateStampViewController.m
//  Stamped
//
//  Created by Devin Doty on 6/12/12.
//
//

#import "CreateStampViewController.h"
#import "CreditPickerViewController.h"
#import "PostStampViewController.h"
#import "EntityDetailViewController.h"
#import "CreateFooterView.h"
#import "CreateHeaderView.h"
#import "STStampSwitch.h"
#import "STPostStampViewController.h"
#import "STS3Uploader.h"
#import "STStampContainerView.h"
#import "CreateEditView.h"

#define kEditContainerViewTag 101

@interface CreateStampViewController ()
@property(nonatomic,readonly) CreateHeaderView *headerView; // weak
@property(nonatomic,readonly) CreateFooterView *footerView; // weak
@property(nonatomic,retain) CreateEditView *editView;
@property(nonatomic,retain) STS3Uploader *imageUploader;
@property(nonatomic,copy) NSString *tempImagePath;
@property(nonatomic,retain) id<STEntity> entity;
@property(nonatomic,retain) id<STEntitySearchResult> searchResult;
@property(nonatomic,retain) NSArray *creditUsernames;
@property(nonatomic,retain) EntityDetailViewController *todoViewController;
@property(nonatomic,retain) UIButton *todoStampButton;
@end

@implementation CreateStampViewController
@synthesize headerView=_headerView;
@synthesize footerView=_footerView;
@synthesize editView=_editView;
@synthesize entity=_entity;
@synthesize searchResult=_searchResult;
@synthesize imageUploader;
@synthesize tempImagePath;
@synthesize creditUsernames;
@synthesize todoViewController;
@synthesize todoStampButton;

- (void)commonInit {
    
    self.imageUploader = [[STS3Uploader alloc] init];
    self.title = @"New Stamp";
    
}

- (id)initWithEntity:(id)entity {
    
    if ((self = [super initWithStyle:UITableViewStylePlain])) {
        [self commonInit];
    }
    return self;
    
}

- (id)initWithSearchResult:(id<STEntitySearchResult>)searchResult {
    
    if ((self = [super initWithStyle:UITableViewStylePlain])) {
        [self commonInit];
        self.searchResult = searchResult;
    }
    return self;
    
}

- (void)dealloc {
    _headerView=nil;
    _footerView=nil;
    self.tempImagePath=nil;
    self.editView=nil;
    self.searchResult=nil;
    self.entity=nil;
    self.imageUploader=nil;
    self.creditUsernames=nil;
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
    self.tableView.allowsSelection = NO;
    self.tableView.rowHeight = 270;
    
    STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.tableView.bounds];
    background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    [background setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
        drawGradient([UIColor colorWithRed:0.99f green:0.99f blue:0.99f alpha:1.0f].CGColor, [UIColor colorWithRed:0.898f green:0.898f blue:0.898f alpha:1.0f].CGColor, ctx);
    }];
    self.tableView.backgroundView = background;
    [background release];
    
    if (!self.navigationItem.rightBarButtonItem) {
        STStampSwitch *control = [[STStampSwitch alloc] initWithFrame:CGRectZero];
        [control addTarget:self action:@selector(switchToggled:) forControlEvents:UIControlEventValueChanged];
        UIBarButtonItem *item = [[UIBarButtonItem alloc] initWithCustomView:control];
        [control release];
        self.navigationItem.rightBarButtonItem = item;
        [item release];
    }
    
    STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:@"Cancel" style:UIBarButtonItemStyleBordered target:self action:@selector(cancel:)];
    self.navigationItem.leftBarButtonItem = button;
    [button release];
    
    if (!_headerView) {
        CreateHeaderView *view = [[CreateHeaderView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 60.0f)];
        [view addTarget:self action:@selector(headerTapped:) forControlEvents:UIControlEventTouchUpInside];
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        self.tableView.tableHeaderView = view;
        [view setupWithItem:self.entity==nil ? (id)self.searchResult : (id)self.entity];
        _headerView = view;
        [view release];
    }
    
    if (!_footerView) {
        CreateFooterView *view = [[CreateFooterView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 84.0f)];
        view.delegate = (id<CreateFooterViewDelegate>)self;
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        self.tableView.tableFooterView = view;
        _footerView = view;
        [view release];
    }
    
}

- (void)viewDidUnload {
    
    _headerView=nil;
    [super viewDidUnload];
}


#pragma mark - Actions

- (void)switchToggled:(STStampSwitch*)sender {
    
    self.title = [sender isOn] ? @"New To-do" : @"New Stamp";
    [self.navigationController.navigationBar setNeedsDisplay];
    
    sender.userInteractionEnabled = NO;
    
    if ([sender isOn]) {
        
        if (self.todoViewController) return;
        
        __block EntityDetailViewController *controller;
        if (self.searchResult) {
            controller = [[EntityDetailViewController alloc] initWithSearchID:self.searchResult.searchID];
        } else {
            controller = [[EntityDetailViewController alloc] initWithEntityID:self.entity.entityID];
        }
        
        __block UIView *view = controller.view;
        [self.view addSubview:view];
        [controller.toolbar setHidden:YES];

        CGRect frame = self.view.bounds;
        frame.origin.y = self.view.bounds.size.height;
        view.frame = frame;
        frame.origin.y = 0.0f;
        self.todoViewController = controller;
        [controller release];
        
        UIImage *image = [UIImage imageNamed:@"create_stamp_btn.png"];
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        [button addTarget:self action:@selector(addTodo:) forControlEvents:UIControlEventTouchUpInside];
        button.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleTopMargin;
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:image.size.height] forState:UIControlStateNormal];
        button.titleLabel.font = [UIFont boldSystemFontOfSize:12];
        [button setTitleColor:[UIColor whiteColor] forState:UIControlStateNormal];
        [button setTitle:@"Add To-Do" forState:UIControlStateNormal];
        [view addSubview:button];
        button.frame = CGRectMake((frame.size.width-106.0f), frame.size.height - (image.size.height+8.0f), 96.0f, image.size.height);
        self.todoStampButton = button;
        
        [UIView animateWithDuration:0.3f animations:^{
        
            view.frame = frame;
            
        } completion:^(BOOL finished) {
            sender.userInteractionEnabled = YES;
        }];

        
    } else {
        
        if (self.todoViewController) {
            
            __block UIView *view = self.todoViewController.view;
            CGRect frame = self.view.bounds;
            frame.origin.y = self.view.bounds.size.height;

            [UIView animateWithDuration:0.3f animations:^{
                
                view.frame = frame;
                
            } completion:^(BOOL finished) {
                
                [self.todoStampButton removeFromSuperview];
                self.todoStampButton = nil;

                [view removeFromSuperview];
                self.todoViewController = nil;
                sender.userInteractionEnabled = YES;

            }];
        }
        
        
    }
    
    
    
    
}

- (void)cancel:(id)sender {
    
    UIActionSheet *actionSheet = [[UIActionSheet alloc] initWithTitle:@"Are you sure you want to delete this Stamp?" delegate:(id<UIActionSheetDelegate>)self cancelButtonTitle:@"Cancel" destructiveButtonTitle:@"Delete Stamp" otherButtonTitles:nil];
    actionSheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
    [actionSheet showInView:self.view];
    [actionSheet release];
    
}

- (void)addTodo:(id)sender {
    
    STStampSwitch *stampSwitch = (STStampSwitch*)self.navigationItem.rightBarButtonItem.customView;
    stampSwitch.on = NO;
    
}

- (void)headerTapped:(id)sender {
    
    EntityDetailViewController *controller;
    if (self.searchResult) {
        controller = [[EntityDetailViewController alloc] initWithSearchID:self.searchResult.searchID];
    } else {
        controller = [[EntityDetailViewController alloc] initWithEntityID:self.entity.entityID];
    }
    [self.navigationController pushViewController:controller animated:YES];
    [controller release];
    
}


#pragma mark - CreditPickerViewControllerDelegate

- (void)creditPickerViewController:(CreditPickerViewController*)controller doneWithUsernames:(NSArray*)usernames {
    
    self.creditUsernames = usernames;
    [self.editView setupWithCreditUsernames:self.creditUsernames];
    [self dismissModalViewControllerAnimated:YES];

}

- (void)creditPickerViewControllerCancelled:(CreditPickerViewController*)controller {
    [self dismissModalViewControllerAnimated:YES];
}


#pragma mark - CreateFooterViewDelegate

- (void)createFooterView:(CreateFooterView*)view twitterSelected:(UIButton*)button {
    button.selected = !button.selected;
}

- (void)createFooterView:(CreateFooterView*)view facebookSelected:(UIButton*)button {
    button.selected = !button.selected;
}

- (void)createFooterView:(CreateFooterView*)view stampIt:(UIButton*)button {
    
    self.view.userInteractionEnabled = NO;
    UIActivityIndicatorView *activityView = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleWhite];
    [button addSubview:activityView];
    [activityView startAnimating];
    activityView.layer.position = CGPointMake((button.bounds.size.width/2), button.bounds.size.height/2);
    [activityView release];
    button.titleLabel.alpha = 0.0f;
        
    STStampNew *stampNew = [[[STStampNew alloc] init] autorelease];
    stampNew.blurb = self.editView.textView.text;
    stampNew.entityID = self.entity.entityID;
    stampNew.searchID = self.searchResult.searchID;
    stampNew.tempImageURL = self.tempImagePath;
    
    if (self.creditUsernames && [self.creditUsernames count] > 0) {
        stampNew.credit = [self.creditUsernames componentsJoinedByString:@","];
    }

    [[STStampedAPI sharedInstance] createStampWithStampNew:stampNew andCallback:^(id<STStamp> stamp, NSError *error, STCancellation* cancellation) {
        
        if (stamp) {
            
           // PostStampViewController *controller = [[[PostStampViewController alloc] initWithStamp:stamp] autorelease];
            STPostStampViewController *controller = [[[STPostStampViewController alloc] initWithStamp:stamp] autorelease];
            controller.navigationItem.hidesBackButton = YES;
            [self.navigationController pushViewController:controller animated:YES];
            
        } else {
            
            [activityView removeFromSuperview];
            button.titleLabel.alpha = 1.0f;
            self.view.userInteractionEnabled = YES;
            
        }
        
    }];
    
}


#pragma mark - CreateEditViewDelegate

- (void)createEditViewSelectedCreditPicker:(CreateEditView*)view {
    
    CreditPickerViewController *controller = [[CreditPickerViewController alloc] initWithEntityIdentifier:(self.entity==nil) ? self.searchResult.searchID : self.entity.entityID];
    controller.delegate = (id<CreditPickerViewControllerDelegate>)self;
    STRootViewController *navContorller = [[STRootViewController alloc] initWithRootViewController:controller];
    [self presentModalViewController:navContorller animated:YES];
    [controller release];
    [navContorller release];
    
}

- (void)createEditView:(CreateEditView*)view addPhotoWithSourceType:(UIImagePickerControllerSourceType)source {
    
    UIImagePickerController *controller = [[UIImagePickerController alloc] init];
    controller.allowsEditing = YES;
    controller.delegate = (id<UIImagePickerControllerDelegate, UINavigationControllerDelegate>)self;
    if ([UIImagePickerController isSourceTypeAvailable:source]) {
        controller.sourceType = source;
    }
    [self presentModalViewController:controller animated:YES];
    
}


#pragma mark - CreateEditViewDataSource

- (UIView*)createEditViewSuperview:(CreateEditView*)view {
    
    if (view.editing) {
        
        if (self.navigationController) {
            return self.navigationController.view;
        }
        return self.view;
        
    }
    
    return [self.tableView viewWithTag:kEditContainerViewTag];
   
}


#pragma mark - UIActionSheetDelegate

- (void)actionSheet:(UIActionSheet *)actionSheet clickedButtonAtIndex:(NSInteger)buttonIndex {
    if (actionSheet.cancelButtonIndex == buttonIndex) return;
    [self dismissModalViewControllerAnimated:YES];
}


#pragma mark - UITableViewDataSource

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    return 1;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    UITableViewCell *cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:nil] autorelease];
    
    STStampContainerView *view = [[[STStampContainerView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.tableView.bounds.size.width, 270.0f)] autorelease];
    view.tag = kEditContainerViewTag;
    view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
    [cell addSubview:view];

    CreateEditView *editView = [[[CreateEditView alloc] initWithFrame:CGRectInset(view.bounds, 5.0f, 10.0f)] autorelease];
    editView.dataSource = (id<CreateEditViewDataSource>)self;
    editView.delegate = (id<CreateEditViewDelegate,UIScrollViewDelegate>)self;
    [view addSubview:editView];
    self.editView = editView;    
    
    return cell;
    
}


#pragma mark - UIImagePickerControllerDelegate

- (void)imagePickerController:(UIImagePickerController *)picker didFinishPickingMediaWithInfo:(NSDictionary *)info {
    
    [self.imageUploader cancel];
    [picker dismissModalViewControllerAnimated:YES];    
   
    if ([info objectForKey:@"UIImagePickerControllerEditedImage"]) {
        
        UIImage *image = [info objectForKey:UIImagePickerControllerEditedImage];
        image = [image aspectScaleToSize:CGSizeMake(500.0f, 500.0f)];

        NSString *path = [NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES) objectAtIndex:0];
		path = [[path stringByAppendingPathComponent:[[NSProcessInfo processInfo] processName]] stringByAppendingPathComponent:@"UploadTemp"];
        [[NSFileManager defaultManager] createDirectoryAtPath:path withIntermediateDirectories:YES attributes:nil error:nil];
        path = [path stringByAppendingPathComponent:@"temp.jpg"];
        [[NSFileManager defaultManager] removeItemAtPath:path error:nil];
        [UIImageJPEGRepresentation(image, 0.85) writeToFile:path atomically:NO];
        self.imageUploader.filePath = path;
              
        self.editView.imageView.image = image;
        [self.editView.imageView setUploading:YES];
        [self.editView layoutScrollView];
        
        [self.footerView setUploading:YES animated:YES];
        [self.imageUploader startWithProgress:^(float progress) {
            
        } completion:^(NSString *path, BOOL finished) {
            
            [self.footerView setUploading:NO animated:YES];
            self.tempImagePath = path;
            [self.editView.imageView setUploading:NO];

        }];
        
    }
    
}

- (void)imagePickerControllerDidCancel:(UIImagePickerController*)controller {
    [controller dismissModalViewControllerAnimated:YES];
}


@end
