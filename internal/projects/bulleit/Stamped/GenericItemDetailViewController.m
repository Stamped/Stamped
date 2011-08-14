//
//  GenericItemDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/10/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "GenericItemDetailViewController.h"

@implementation GenericItemDetailViewController

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  self.scrollView.contentSize = CGSizeMake(self.view.bounds.size.width, 480);
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
}

- (IBAction)mainActionButtonPressed:(id)sender {
  [[UIApplication sharedApplication] openURL:
      [NSURL URLWithString:@"itms://itunes.apple.com/us/album/wolfgang-amadeus-phoenix/id315002203"]];
}

@end
