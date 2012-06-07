//
//  STSettingsViewController.m
//  Stamped
//
//  Created by Devin Doty on 6/7/12.
//
//

#import "STSettingsViewController.h"

@interface STSettingsViewController ()

@end

@implementation STSettingsViewController

- (id)init {
    
    if ((self = [super init])) {
        self.title = NSLocalizedString(@"Settings", @"Settings");
    }
    return self;
    
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.view.bounds];
    background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    [background setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
        drawGradient([UIColor colorWithRed:0.961f green:0.961f blue:0.957f alpha:1.0f].CGColor, [UIColor colorWithRed:0.898f green:0.898f blue:0.898f alpha:1.0f].CGColor, ctx);
    }];
    [self.view addSubview:background];
    [background release];
    
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
}


#pragma mark - UITableViewDataSource

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    
    return 0;
    
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    static NSString *CellIdentifier = @"CellIdentifier";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell =[[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }
    
    return cell;
    
}


@end
