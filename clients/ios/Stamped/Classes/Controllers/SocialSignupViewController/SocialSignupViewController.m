//
//  SocialSignupViewController.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "SocialSignupViewController.h"
#import "StampColorPickerView.h"
#import "SocialSignupHeaderView.h"
#import "STTextFieldTableCell.h"
#import "StampCustomizeViewController.h"
#import "StampCustomizerViewController.h"

@interface SocialSignupViewController ()
@end

@implementation SocialSignupViewController
@synthesize tableView=_tableView;

- (id)init {
    if ((self = [super init])) {
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(keyboardWillShow:) name:UIKeyboardWillShowNotification  object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(keyboardWillHide:) name:UIKeyboardWillHideNotification object:nil];
    }
    return self;
}

- (void)dealloc {
    self.tableView = nil;
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    if (!_tableView) {
        
        UITableView *tableView = [[UITableView alloc] initWithFrame:self.view.bounds style:UITableViewStyleGrouped];
        tableView.showsVerticalScrollIndicator = NO;
        tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
        tableView.allowsSelection = NO;
        tableView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        tableView.delegate = (id<UITableViewDelegate>)self;
        tableView.dataSource = (id<UITableViewDataSource>)self;
        [self.view addSubview:tableView];
        self.tableView = tableView;
        [tableView release];
        
        SocialSignupHeaderView *header = [[SocialSignupHeaderView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 104.0f)];
        header.backgroundColor = [UIColor clearColor];
        tableView.tableHeaderView = header;
        [header release];
        
        StampColorPickerView *view = [[StampColorPickerView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 220.0f)];
        view.backgroundColor = [UIColor clearColor];
        view.delegate = (id<StampColorPickerDelegate>)self;
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        tableView.tableFooterView = view;
        [view release];
        
        STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:tableView.bounds];
        background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        [background setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
            drawGradient([UIColor colorWithRed:0.961f green:0.961f blue:0.957f alpha:1.0f].CGColor, [UIColor colorWithRed:0.898f green:0.898f blue:0.898f alpha:1.0f].CGColor, ctx);
        }];
        tableView.backgroundView = background;
        [background release];
        
    }
    
    if (!self.navigationItem.rightBarButtonItem) {
        
        STNavigationItem *item = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Next", @"Next") style:UIBarButtonItemStyleBordered target:self action:@selector(next:)];
        self.navigationItem.rightBarButtonItem = item;
        [item release];
        
    }
    
    
}

- (void)viewDidUnload {
    self.tableView = nil;
    [super viewDidUnload];
}


#pragma mark - Actions

- (void)next:(id)sender {
    
    
    
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
    
    StampCustomizeViewController *controller = [[StampCustomizeViewController alloc] init];
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


#pragma mark - UIKeyboard Notfications

- (void)keyboardWillShow:(NSNotification*)notification {    
    
    CGRect keyboardFrame = [[[notification userInfo] objectForKey:UIKeyboardFrameEndUserInfoKey] CGRectValue];
    [UIView animateWithDuration:0.3 delay:0 options:UIViewAnimationCurveEaseOut animations:^{
        self.tableView.contentInset = UIEdgeInsetsMake(0, 0, keyboardFrame.size.height, 0);
    } completion:^(BOOL finished){}];
    
}

- (void)keyboardWillHide:(NSNotification*)notification {
    
    [UIView animateWithDuration:0.3 animations:^{
        self.tableView.contentInset = UIEdgeInsetsZero;
    }];
    
}


#pragma mark - UITextFieldDelegate

- (BOOL)textFieldShouldReturn:(UITextField *)textField {
    [textField resignFirstResponder];
    return YES;
}


@end
