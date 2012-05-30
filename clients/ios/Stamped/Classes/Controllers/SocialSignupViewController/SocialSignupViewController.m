//
//  SocialSignupViewController.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "SocialSignupViewController.h"
#import "StampColorPickerView.h"

@interface SocialSignupViewController ()
@end

@implementation SocialSignupViewController
@synthesize tableView=_tableView;

- (id)init {
    if ((self = [super init])) {
        
    }
    return self;
}

- (void)dealloc {
    self.tableView = nil;
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    if (!_tableView) {
        
        UITableView *tableView = [[UITableView alloc] initWithFrame:self.view.bounds style:UITableViewStyleGrouped];
        tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
        tableView.allowsSelection = NO;
        tableView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        tableView.delegate = (id<UITableViewDelegate>)self;
        tableView.dataSource = (id<UITableViewDataSource>)self;
        [self.view addSubview:tableView];
        self.tableView = tableView;
        [tableView release];
        
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
    
    if (indexPath.row == 2) {
        return 200.0f;
    }
    
    return 100.0f;
    
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    return 2;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    static NSString *CellIdentifier = @"CellIDentifier";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }
    
    if (indexPath.row == 1) {
        
        StampColorPickerView *view = [[StampColorPickerView alloc] initWithFrame:cell.bounds];
        view.backgroundColor = [UIColor clearColor];
        view.delegate = (id<StampColorPickerDelegate>)self;
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        [cell addSubview:view];
        [view release];
        
        
    }
    
    return cell;
    
}

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
    
    return 30.0f;
    
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
    
    UIView *view = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, tableView.bounds.size.width, 30.0f)];
    
    UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
    label.textColor = [UIColor colorWithRed:0.600f green:0.600f blue:0.600f alpha:1.0f];
    label.shadowColor = [UIColor whiteColor];
    label.shadowOffset = CGSizeMake(0.0f, 1.0f);
    label.font = [UIFont boldSystemFontOfSize:12];
    
    if (section == 0) {
        label.text = @"Create your username";
    } else if (section == 1) {
        label.text = @"Choose your stamp color";
    }
    
    [label sizeToFit];
    CGRect frame = label.frame;
    frame.origin.x = 10.0f;
    frame.origin.y = floorf((view.bounds.size.height-frame.size.height)/2);
    label.frame = frame;
    [view addSubview:label];
    [label release];
    
    return [view autorelease];
    
}


#pragma mark - StampColorPickerDelegate


@end
