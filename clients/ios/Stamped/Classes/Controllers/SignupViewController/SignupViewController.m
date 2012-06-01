//
//  SignupViewController.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "SignupViewController.h"
#import "STTextFieldTableCell.h"

@interface SignupViewController ()

@end

@implementation SignupViewController
@synthesize delegate;

- (id)init {
    if (self = [super initWithStyle:UITableViewStyleGrouped]) {
        _dataSource = [[NSArray arrayWithObjects:@"full name", @"email", @"username", @"password", @"phone number", nil] retain];
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
    
    if (!self.tableView.backgroundView) {
        STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.tableView.bounds];
        background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        [background setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
            drawGradient([UIColor colorWithRed:0.961f green:0.961f blue:0.957f alpha:1.0f].CGColor, [UIColor colorWithRed:0.898f green:0.898f blue:0.898f alpha:1.0f].CGColor, ctx);
        }];
        self.tableView.backgroundView = background;
        [background release];
    }
    
    self.tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
    
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
}


#pragma mark - Actions

- (void)cancel:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(signupViewControllerCancelled:)]) {
        [self.delegate signupViewControllerCancelled:self];
    }
    
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
        cell.textField.returnKeyType = UIReturnKeyNext;
        cell.textField.autocapitalizationType = UITextAutocapitalizationTypeNone;
        cell.textField.autocorrectionType = UITextAutocorrectionTypeNo;
    }
    cell.titleLabel.text = [_dataSource objectAtIndex:indexPath.row];
    return cell;
    
}


#pragma mark - UITextFieldDelegate

- (BOOL)textFieldShouldReturn:(UITextField *)textField {
    
    
    return YES;
}

@end
