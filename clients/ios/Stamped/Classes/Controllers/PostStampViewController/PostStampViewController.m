//
//  PostStampViewController.m
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import "PostStampViewController.h"
#import "PostStampGraphView.h"
#import "CreateHeaderView.h"

@interface PostStampViewController ()
@property(nonatomic,strong) CreateHeaderView *headerView;
@property(nonatomic,strong) PostStampGraphView *graphView;
@property(nonatomic,assign) id<STStamp> stamp;
@end

@implementation PostStampViewController
@synthesize graphView=_graphView;
@synthesize headerView=_headerView;
@synthesize stamp=_stamp;


- (id)initWithStamp:(id<STStamp>)stamp {
    if ((self = [super init])) {
        self.title = NSLocalizedString(@"Your stamp", @"Your stamp");
        _stamp = [stamp retain];
    }
    return self;
}

- (void)dealloc {
    self.graphView = nil;
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    if (!_graphView) {
        PostStampGraphView *view = [[PostStampGraphView alloc] initWithFrame:CGRectMake(0.0f, 100.0f, self.view.bounds.size.width, 100.0f)];
        [self.view addSubview:view];
        self.graphView = view;
        [view release];
    }
    
    if (!_headerView) {
        CreateHeaderView *view = [[CreateHeaderView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 60.0f)];
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        _headerView = view;
        [view release];
    }
    
    STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Done", @"Done") style:UIBarButtonItemStyleDone target:self action:@selector(done:)];
    self.navigationItem.rightBarButtonItem = button;
    [button release];

}

- (void)viewDidUnload {
    self.graphView = nil;
    [super viewDidUnload];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
}


@end
