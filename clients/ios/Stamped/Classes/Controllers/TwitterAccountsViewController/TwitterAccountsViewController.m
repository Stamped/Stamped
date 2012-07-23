//
//  TwitterAccountsViewController.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "TwitterAccountsViewController.h"
#import "STSingleTableCell.h"
#import "STBlockUIView.h"
#import "QuartzUtils.h"
#import "STTwitter.h"
#import "STAuth.h"
#import "SignupWelcomeViewController.h"
#import "STEvents.h"
#import "STNavigationItem.h"
#import "STDebug.h"


@interface TwitterAccountsViewController ()
@property (nonatomic,strong) UITableView *tableView;
@end

@implementation TwitterAccountsViewController
@synthesize tableView=_tableView;
@synthesize delegate;

- (id)init {
    if ((self = [super init])) {
        [STEvents addObserver:self selector:@selector(twitterAuthFinished:) event:EventTypeTwitterAuthFinished];
        [STEvents addObserver:self selector:@selector(twitterAuthFailed:) event:EventTypeTwitterAuthFailed];
    }
    return self;
}

- (void)dealloc {
    self.tableView = nil;
    [STEvents removeObserver:self];
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    
    if (!self.navigationItem.leftBarButtonItem) {
        STNavigationItem *item = [[STNavigationItem alloc] initWithTitle:@"Cancel" style:UIBarButtonItemStyleBordered target:self action:@selector(cancel:)];
        self.navigationItem.leftBarButtonItem = item;
        [item release];
    }

    if (!_tableView) {
        
        UITableView *tableView = [[UITableView alloc] initWithFrame:self.view.bounds style:UITableViewStyleGrouped];
        tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
        tableView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        tableView.delegate = (id<UITableViewDelegate>)self;
        tableView.dataSource = (id<UITableViewDataSource>)self;
        [self.view addSubview:tableView];
        self.tableView = tableView;
        [tableView release];
        
        STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:tableView.bounds];
        background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        [background setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
            drawGradient([UIColor colorWithRed:0.961f green:0.961f blue:0.957f alpha:1.0f].CGColor, [UIColor colorWithRed:0.898f green:0.898f blue:0.898f alpha:1.0f].CGColor, ctx);
        }];
        tableView.backgroundView = background;
        [background release];
         
        UIView *header = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 50.0f)];
        header.backgroundColor = [UIColor clearColor];
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin;
        label.text = @"Tap your account to sign in";
        label.font = [UIFont boldSystemFontOfSize:16];
        label.textColor = [UIColor colorWithRed:0.600f green:0.600f blue:0.600f alpha:1.0f];
        label.backgroundColor = [UIColor clearColor];
        [header addSubview:label];
        [label sizeToFit];
        
        CGRect frame = label.frame;
        frame.origin.x = floorf((header.bounds.size.width-frame.size.width)/2);
        frame.origin.y = floorf(header.bounds.size.height-(frame.size.height+4.0f));
        label.frame = frame;
        [label release];
        
        tableView.tableHeaderView = header;
        [header release];
        
        UIView *footer = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 100.0f)];
        footer.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        footer.backgroundColor = [UIColor clearColor];
        
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"login_twitter_bird.png"]];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleRightMargin;
        [footer addSubview:imageView];
        frame = imageView.frame;
        frame.origin.x = (footer.bounds.size.width-frame.size.width)/2;
        frame.origin.y = (footer.bounds.size.height-frame.size.height)/2;
        imageView.frame = frame;
        
        tableView.tableFooterView = footer;
        [footer release];
        [imageView release];
        
    }
    
    [[STTwitter sharedInstance] requestAccess:^(BOOL granted) {
        [self.tableView reloadData];
    }];
    

}

- (void)viewDidUnload {
    self.tableView = nil;
    [super viewDidUnload];
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    [self.tableView deselectRowAtIndexPath:self.tableView.indexPathForSelectedRow animated:animated];
}


#pragma mark - Actions

- (void)cancel:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(twitterAccountsViewControllerCancelled:)]) {
        [self.delegate twitterAccountsViewControllerCancelled:self];
    }
    
}


#pragma mark - Signup

- (void)signupTwitter {
    
    [STEvents removeObserver:self];
    [[STTwitter sharedInstance] getTwitterUser:^(id user, NSError *error) {
        
        if (user && !error) {
            [[STTwitter sharedInstance] setTwitterUser:user];
            SignupWelcomeViewController *controller = [[SignupWelcomeViewController alloc] initWithType:SignupWelcomeTypeTwitter];
            controller.navigationItem.hidesBackButton = YES;
            double delayInSeconds = 0.1f;
            dispatch_time_t popTime = dispatch_time(DISPATCH_TIME_NOW, delayInSeconds * NSEC_PER_SEC);
            dispatch_after(popTime, dispatch_get_main_queue(), ^(void){
                [self.navigationController pushViewController:controller animated:YES];
                [controller release];
            });
        }
        
    }];
    
}


#pragma mark - Notifications 

- (void)twitterAuthFinished:(NSNotification*)notification {
    
    [[STAuth sharedInstance] twitterAuthWithToken:[[STTwitter sharedInstance] twitterToken] secretToken:[[STTwitter sharedInstance] twitterTokenSecret] completion:^(NSError *error) {
        
        if (error) {
            
            [self signupTwitter];
            STSingleTableCell *cell = (STSingleTableCell*)[self.tableView cellForRowAtIndexPath:self.tableView.indexPathForSelectedRow];
            if (cell) {
                [cell setLoading:YES];
                self.view.userInteractionEnabled = NO;
            }
            [self.tableView deselectRowAtIndexPath:self.tableView.indexPathForSelectedRow animated:YES];
            
        } else {
            
            if ([(id)delegate respondsToSelector:@selector(twitterAccountsViewControllerSuccessful:)]) {
                [self.delegate twitterAccountsViewControllerSuccessful:self];
            }
            
        }
        
    }];
    

    
}

- (void)twitterAuthFailed:(NSNotification*)notification {
    
    STSingleTableCell *cell = (STSingleTableCell*)[self.tableView cellForRowAtIndexPath:self.tableView.indexPathForSelectedRow];
    if (cell) {
        [cell setLoading:YES];
        self.view.userInteractionEnabled = NO;
    }
    [self.tableView deselectRowAtIndexPath:self.tableView.indexPathForSelectedRow animated:YES];
    
    [STDebug log:@"twitter auth failed"];
}


#pragma mark - UITableViewDataSource

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    return [STSingleTableCell height];

}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    return [[STTwitter sharedInstance] numberOfAccounts];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    static NSString *CellIdentifier = @"CellIdentifier";
    
    STSingleTableCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[[STSingleTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
        cell.titleLabel.textAlignment = UITextAlignmentCenter;
    }
    
    ACAccount *account = [[STTwitter sharedInstance] accountAtIndex:indexPath.row];
    cell.titleLabel.text = [NSString stringWithFormat:@"@%@", account.username];
    
    return cell;
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    
    ACAccount *account = [[STTwitter sharedInstance] accountAtIndex:indexPath.row];
    [[STTwitter sharedInstance] reverseAuthWithAccount:account];
    
    STSingleTableCell *cell = (STSingleTableCell*)[tableView cellForRowAtIndexPath:indexPath];
    [cell setLoading:YES];
    self.view.userInteractionEnabled = NO;
        
}


@end
