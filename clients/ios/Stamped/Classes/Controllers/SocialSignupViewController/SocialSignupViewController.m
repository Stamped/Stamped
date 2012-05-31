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

- (id)init {
    if ((self = [super initWithStyle:UITableViewStyleGrouped])) {
    }
    return self;
}

- (void)dealloc {
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.tableView.showsVerticalScrollIndicator = NO;
    self.tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
    self.tableView.allowsSelection = NO;
    
    if (!self.tableView.tableHeaderView) {
        SocialSignupHeaderView *header = [[SocialSignupHeaderView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 104.0f)];
        header.backgroundColor = [UIColor clearColor];
        self.tableView.tableHeaderView = header;
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
    
    
}

- (void)viewDidUnload {
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
